// Copyright (c) 2002, Xiph.org Foundation. See COPYING (BSD license).
// Setup/ownership code adapted from Xiph.Org Tremor; see README.md.
// Decode, synthesis, MDCT, window and PCM arithmetic remain in the pinned archive.
#include "../vorbis_repair_abi.h"
#include "esp_vorbis_dec.h"
#include <limits.h>
#include <stdlib.h>
#include <string.h>
extern void *media_lib_module_calloc(const char *, size_t, size_t);
extern void media_lib_free(void *);
static void *repair_alloc(size_t bytes) {
    return bytes ? media_lib_module_calloc("AUD_Codec", 1, bytes) : NULL;
}
static void *repair_calloc(size_t count, size_t bytes) {
    return bytes && count <= SIZE_MAX / bytes ? repair_alloc(count * bytes) : NULL;
}
enum { VI_FLOORB = 2, OV_EFAULT = -129, OV_EVERSION = -134, OV_EBADHEADER = -133 };
static int repair__vorbis_unpack_books(vorbis_info *, oggpack_buffer *);
static int _ilog(unsigned int v){
  int ret=0;
  while(v){
    ret++;
    v>>=1;
  }
  return(ret);
}

static ogg_uint32_t decpack(long entry,long used_entry,long quantvals,
			    codebook *b,oggpack_buffer *opb,int maptype){
  ogg_uint32_t ret=0;
  int j;
  
  switch(b->dec_type){

  case 0:
    return (ogg_uint32_t)entry;

  case 1:
    if(maptype==1){
      /* vals are already read into temporary column vector here */
      for(j=0;j<b->dim;j++){
	ogg_uint32_t off=entry%quantvals;
	entry/=quantvals;
	ret|=((ogg_uint16_t *)(b->q_val))[off]<<(b->q_bits*j);
      }
    }else{
      for(j=0;j<b->dim;j++)
	ret|=tremor_oggpack_read(opb,b->q_bits)<<(b->q_bits*j);
    }
    return ret;
    
  case 2:
    for(j=0;j<b->dim;j++){
      ogg_uint32_t off=entry%quantvals;
      entry/=quantvals;
      ret|=off<<(b->q_pack*j);
    }
    return ret;

  case 3:
    return (ogg_uint32_t)used_entry;

  }
  return 0; /* silence compiler */
}

/* 32 bit float (not IEEE; nonnormalized mantissa +
   biased exponent) : neeeeeee eeemmmmm mmmmmmmm mmmmmmmm 
   Why not IEEE?  It's just not that important here. */

static ogg_int32_t _float32_unpack(long val,int *point){
  long   mant=val&0x1fffff;
  int    sign=val&0x80000000;
  
  *point=((val&0x7fe00000L)>>21)-788;

  if(mant){
    while(!(mant&0x40000000)){
      mant<<=1;
      *point-=1;
    }
    if(sign)mant= -mant;
  }else{
    *point=-9999;
  }
  return mant;
}

/* choose the smallest supported node size that fits our decode table.
   Legal bytewidths are 1/1 1/2 2/2 2/4 4/4 */
static int _determine_node_bytes(long used, int leafwidth){

  /* special case small books to size 4 to avoid multiple special
     cases in repack */
  if(used<2)
    return 4;

  if(leafwidth==3)leafwidth=4;
  if(_ilog(3*used-6)+1 <= leafwidth*4) 
    return leafwidth/2?leafwidth/2:1;
  return leafwidth;
}

/* convenience/clarity; leaves are specified as multiple of node word
   size (1 or 2) */
static int _determine_leaf_words(int nodeb, int leafwidth){
  if(leafwidth>nodeb)return 2;
  return 1;
}

/* given a list of word lengths, number of used entries, and byte
   width of a leaf, generate the decode table */
static int _make_words(char *l,long n,ogg_uint32_t *r,long quantvals,
		       codebook *b, oggpack_buffer *opb,int maptype,
                       size_t table_words){
  long i,j,count=0;
  long top=0;
  ogg_uint32_t marker[33];

  if (n<1)
    return 1;

  if(n<2){
    r[0]=0x80000000;
  }else{
    memset(marker,0,sizeof(marker));
    
    for(i=0;i<n;i++){
      long length=l[i];
      if(length){
	ogg_uint32_t entry=marker[length];
	long chase=0;
	if(count && !entry)return -1; /* overpopulated tree! */
	
	/* chase the tree as far as it's already populated, fill in past */
	for(j=0;j<length-1;j++){
	  int bit=(entry>>(length-j-1))&1;
          /* Length-list entries include unused leaves; output capacity is
           * based on used leaves. Check every node before either write. */
          if (chase < 0 || (size_t)chase >= table_words / 2) return 1;
	  if(chase>=top){ 
	    top++;
	    r[chase*2]=top;
	    r[chase*2+1]=0;
	  }
	    if(!r[chase*2+bit])
	      r[chase*2+bit]=top;
	  chase=r[chase*2+bit];
	}
	{	
	  int bit=(entry>>(length-j-1))&1;
          if (chase < 0 || (size_t)chase >= table_words / 2) return 1;
	  if(chase>=top){ 
	    top++;
	    r[chase*2+1]=0;
	  }
	  r[chase*2+bit]= decpack(i,count++,quantvals,b,opb,maptype) | 
	    0x80000000;
	}

	/* Look to see if the next shorter marker points to the node
	   above. if so, update it and repeat.  */
	for(j=length;j>0;j--){          
	  if(marker[j]&1){
	    marker[j]=marker[j-1]<<1;
	    break;
	  }
	  marker[j]++;
	}
	
	/* prune the tree; the implicit invariant says all the longer
	   markers were dangling from our just-taken node.  Dangle them
	   from our *new* node. */
	for(j=length+1;j<33;j++)
	  if((marker[j]>>1) == entry){
	    entry=marker[j];
	    marker[j]=marker[j-1]<<1;
	  }else
	    break;
      }
    }
  }
  
  return 0;
}

static int _make_decode_table(codebook *s,char *lengthlist,long quantvals,
			      oggpack_buffer *opb,int maptype){
  int i;
  ogg_uint32_t *work;

  if (!lengthlist) return 1;
  if(s->dec_nodeb==4){
    size_t table_words=(size_t)s->used_entries*2+1;
    s->dec_table=repair_calloc(table_words,sizeof(*work));
    if (!s->dec_table) return 1;
    /* +1 (rather than -2) is to accommodate 0 and 1 sized books,
       which are specialcased to nodeb==4 */
    if(_make_words(lengthlist,s->entries,
		   s->dec_table,quantvals,s,opb,maptype,table_words))return 1;
    
    return 0;
  }

  if (s->used_entries > INT_MAX/2 ||
      s->used_entries*2 > INT_MAX/((long) sizeof(*work)) - 1) return 1;
  /* A full binary tree with U leaves has U-1 internal nodes, each
   * containing two words. Match the pinned library's workspace size. */
  size_t table_words=(size_t)(s->used_entries-1)*2;
  work=repair_calloc(table_words,sizeof(*work));
  if (!work) return 1;
  if(_make_words(lengthlist,s->entries,work,quantvals,s,opb,maptype,table_words)){ media_lib_free(work); return 1; }
  if (s->used_entries > INT_MAX/(s->dec_leafw+1)){ media_lib_free(work); return 1; }
  if (s->dec_nodeb && s->used_entries * (s->dec_leafw+1) > INT_MAX/s->dec_nodeb){ media_lib_free(work); return 1; }
  s->dec_table=repair_alloc((s->used_entries*(s->dec_leafw+1)-2)*
			   s->dec_nodeb);
  if (!s->dec_table){ media_lib_free(work); return 1; }
  
  if(s->dec_leafw==1){
    switch(s->dec_nodeb){
    case 1:
      for(i=0;i<s->used_entries*2-2;i++)
	  ((unsigned char *)s->dec_table)[i]=
	    ((work[i] & 0x80000000UL) >> 24) | work[i];
      break;
    case 2:
      for(i=0;i<s->used_entries*2-2;i++)
	  ((ogg_uint16_t *)s->dec_table)[i]=
	    ((work[i] & 0x80000000UL) >> 16) | work[i];
      break; 
    }

  }else{
    /* more complex; we have to do a two-pass repack that updates the
       node indexing. */
    long top=s->used_entries*3-2;
    if(s->dec_nodeb==1){
      unsigned char *out=(unsigned char *)s->dec_table;

      for(i=s->used_entries*2-4;i>=0;i-=2){
	if(work[i]&0x80000000UL){
	  if(work[i+1]&0x80000000UL){
	    top-=4;
	    out[top]=(work[i]>>8 & 0x7f)|0x80;
	    out[top+1]=(work[i+1]>>8 & 0x7f)|0x80;
	    out[top+2]=work[i] & 0xff;
	    out[top+3]=work[i+1] & 0xff;
	  }else{
	    top-=3;
	    out[top]=(work[i]>>8 & 0x7f)|0x80;
	    out[top+1]=work[work[i+1]*2];
	    out[top+2]=work[i] & 0xff;
	  }
	}else{
	  if(work[i+1]&0x80000000UL){
	    top-=3;
	    out[top]=work[work[i]*2];
	    out[top+1]=(work[i+1]>>8 & 0x7f)|0x80;
	    out[top+2]=work[i+1] & 0xff;
	  }else{
	    top-=2;
	    out[top]=work[work[i]*2];
	    out[top+1]=work[work[i+1]*2];
	  }
	}
	work[i]=top;
      }
    }else{
      ogg_uint16_t *out=(ogg_uint16_t *)s->dec_table;
      for(i=s->used_entries*2-4;i>=0;i-=2){
	if(work[i]&0x80000000UL){
	  if(work[i+1]&0x80000000UL){
	    top-=4;
	    out[top]=(work[i]>>16 & 0x7fff)|0x8000;
	    out[top+1]=(work[i+1]>>16 & 0x7fff)|0x8000;
	    out[top+2]=work[i] & 0xffff;
	    out[top+3]=work[i+1] & 0xffff;
	  }else{
	    top-=3;
	    out[top]=(work[i]>>16 & 0x7fff)|0x8000;
	    out[top+1]=work[work[i+1]*2];
	    out[top+2]=work[i] & 0xffff;
	  }
	}else{
	  if(work[i+1]&0x80000000UL){
	    top-=3;
	    out[top]=work[work[i]*2];
	    out[top+1]=(work[i+1]>>16 & 0x7fff)|0x8000;
	    out[top+2]=work[i+1] & 0xffff;
	  }else{
	    top-=2;
	    out[top]=work[work[i]*2];
	    out[top+1]=work[work[i+1]*2];
	  }
	}
	work[i]=top;
      }
    }
  }
	
  media_lib_free(work);
  return 0;
}

/* most of the time, entries%dimensions == 0, but we need to be
   well defined.  We define that the possible vales at each
   scalar is values == entries/dim.  If entries%dim != 0, we'll
   have 'too few' values (values*dim<entries), which means that
   we'll have 'left over' entries; left over entries use zeroed
   values (and are wasted).  So don't generate codebooks like
   that */
/* there might be a straightforward one-line way to do the below
   that's portable and totally safe against roundoff, but I haven't
   thought of it.  Therefore, we opt on the side of caution */
static long _book_maptype1_quantvals(codebook *b){
  /* get us a starting hint, we'll polish it below */
  int bits=_ilog(b->entries);
  int vals=b->entries>>((bits-1)*(b->dim-1)/b->dim);

  while(1){
    long acc=1;
    long acc1=1;
    int i;
    for(i=0;i<b->dim;i++){
      acc*=vals;
      acc1*=vals+1;
    }
    if(acc<=b->entries && acc1>b->entries){
      return(vals);
    }else{
      if(acc>b->entries){
        vals--;
      }else{
        vals++;
      }
    }
  }
}

static void repair_vorbis_book_clear(codebook *b){
  /* static book is not cleared; we're likely called on the lookup and
     the static codebook belongs to the info struct */
  if(b->q_val)media_lib_free(b->q_val);
  if(b->dec_table)media_lib_free(b->dec_table);

  memset(b,0,sizeof(*b));
}

static int repair_vorbis_book_unpack(oggpack_buffer *opb,codebook *s){
  char         *lengthlist=NULL;
  int           quantvals=0;
  long          i,j;
  int           maptype;

  memset(s,0,sizeof(*s));

  /* make sure alignment is correct */
  if(tremor_oggpack_read(opb,24)!=0x564342)goto _eofout;

  /* first the basic parameters */
  s->dim=tremor_oggpack_read(opb,16);
  s->entries=tremor_oggpack_read(opb,24);
  if(s->entries<=0)goto _eofout;
  if(s->dim<=0)goto _eofout;
  if(_ilog(s->dim)+_ilog(s->entries)>24)goto _eofout; 
  if (s->dim > INT_MAX/s->entries) goto _eofout;

  /* codeword ordering.... length ordered or unordered? */
  switch((int)tremor_oggpack_read(opb,1)){
  case 0:
    /* unordered */
    lengthlist=(char *)repair_alloc(sizeof(*lengthlist)*s->entries);
    if(!lengthlist) goto _eofout;

    /* allocated but unused entries? */
    if(tremor_oggpack_read(opb,1)){
      /* yes, unused entries */

      for(i=0;i<s->entries;i++){
	if(tremor_oggpack_read(opb,1)){
	  long num=tremor_oggpack_read(opb,5);
	  if(num==-1)goto _eofout;
	  lengthlist[i]=num+1;
	  s->used_entries++;
	  if(num+1>s->dec_maxlength)s->dec_maxlength=num+1;
	}else
	  lengthlist[i]=0;
      }
    }else{
      /* all entries used; no tagging */
      s->used_entries=s->entries;
      for(i=0;i<s->entries;i++){
	long num=tremor_oggpack_read(opb,5);
	if(num==-1)goto _eofout;
	lengthlist[i]=num+1;
	if(num+1>s->dec_maxlength)s->dec_maxlength=num+1;
      }
    }
    
    break;
  case 1:
    /* ordered */
    {
      long length=tremor_oggpack_read(opb,5)+1;

      s->used_entries=s->entries;
      lengthlist=(char *)repair_alloc(sizeof(*lengthlist)*s->entries);
      if (!lengthlist) goto _eofout;
      
      for(i=0;i<s->entries;){
	long num=tremor_oggpack_read(opb,_ilog(s->entries-i));
	if(num<0 || num>s->entries-i || length>32)goto _eofout;
	for(j=0;j<num && i<s->entries;j++,i++)
	  lengthlist[i]=length;
	s->dec_maxlength=length;
	length++;
      }
    }
    break;
  default:
    /* EOF */
    goto _eofout;
  }


  /* Do we have a mapping to unpack? */
  
  if((maptype=tremor_oggpack_read(opb,4))>0){
    s->q_min=_float32_unpack(tremor_oggpack_read(opb,32),&s->q_minp);
    s->q_del=_float32_unpack(tremor_oggpack_read(opb,32),&s->q_delp);
    s->q_bits=tremor_oggpack_read(opb,4)+1;
    s->q_seq=tremor_oggpack_read(opb,1);

    s->q_del>>=s->q_bits;
    s->q_delp+=s->q_bits;
  }

  switch(maptype){
  case 0:

    /* no mapping; decode type 0 */

    /* how many bytes for the indexing? */
    /* this is the correct boundary here; we lose one bit to
       node/leaf mark */
    s->dec_nodeb=_determine_node_bytes(s->used_entries,_ilog(s->entries)/8+1); 
    s->dec_leafw=_determine_leaf_words(s->dec_nodeb,_ilog(s->entries)/8+1); 
    s->dec_type=0;

    if(_make_decode_table(s,lengthlist,quantvals,opb,maptype)) goto _errout;
    break;

  case 1:

    /* mapping type 1; implicit values by lattice  position */
    quantvals=_book_maptype1_quantvals(s);
    
    /* dec_type choices here are 1,2; 3 doesn't make sense */
    {
      /* packed values */
      long total1=(s->q_bits*s->dim+8)/8; /* remember flag bit */
      if (s->dim > (INT_MAX-8)/s->q_bits) goto _eofout;
      /* vector of column offsets; remember flag bit */
      long total2=(_ilog(quantvals-1)*s->dim+8)/8+(s->q_bits+7)/8;

      
      if(total1<=4 && total1<=total2){
	/* use dec_type 1: vector of packed values */

	/* need quantized values before  */
	s->q_val=repair_alloc(sizeof(ogg_uint16_t)*quantvals);
	if (!s->q_val) goto _eofout;
	for(i=0;i<quantvals;i++)
	  ((ogg_uint16_t *)s->q_val)[i]=tremor_oggpack_read(opb,s->q_bits);
	
	if(tremor_oggpack_eop(opb)){
	  /* q_val is heap-owned and cleared by the error path. */
	  goto _eofout;
	}

	s->dec_type=1;
	s->dec_nodeb=_determine_node_bytes(s->used_entries,
					   (s->q_bits*s->dim+8)/8); 
	s->dec_leafw=_determine_leaf_words(s->dec_nodeb,
					   (s->q_bits*s->dim+8)/8); 
	if(_make_decode_table(s,lengthlist,quantvals,opb,maptype)){
	  /* q_val is heap-owned and cleared by the error path. */
	  goto _errout;
	}
	
	media_lib_free(s->q_val);
	s->q_val=0; /* temporary vector consumed; _make_decode_table
                       was using it */
	
      }else{
	/* use dec_type 2: packed vector of column offsets */

	/* need quantized values before */
	if(s->q_bits<=8){
	  s->q_val=repair_alloc(quantvals);
	  if (!s->q_val) goto _eofout;
	  for(i=0;i<quantvals;i++)
	    ((unsigned char *)s->q_val)[i]=tremor_oggpack_read(opb,s->q_bits);
	}else{
	  s->q_val=repair_alloc(quantvals*2);
	  if (!s->q_val) goto _eofout;
	  for(i=0;i<quantvals;i++)
	    ((ogg_uint16_t *)s->q_val)[i]=tremor_oggpack_read(opb,s->q_bits);
	}

	if(tremor_oggpack_eop(opb))goto _eofout;

	s->q_pack=_ilog(quantvals-1); 
	s->dec_type=2;
	s->dec_nodeb=_determine_node_bytes(s->used_entries,
					   (_ilog(quantvals-1)*s->dim+8)/8); 
	s->dec_leafw=_determine_leaf_words(s->dec_nodeb,
					   (_ilog(quantvals-1)*s->dim+8)/8); 
	if(_make_decode_table(s,lengthlist,quantvals,opb,maptype))goto _errout;

      }
    }
    break;
  case 2:

    /* mapping type 2; explicit array of values */
    quantvals=s->entries*s->dim;
    /* dec_type choices here are 1,3; 2 is not possible */

    if( (s->q_bits*s->dim+8)/8 <=4){ /* remember flag bit */
      /* use dec_type 1: vector of packed values */

      s->dec_type=1;
      s->dec_nodeb=_determine_node_bytes(s->used_entries,(s->q_bits*s->dim+8)/8); 
      s->dec_leafw=_determine_leaf_words(s->dec_nodeb,(s->q_bits*s->dim+8)/8); 
      if(_make_decode_table(s,lengthlist,quantvals,opb,maptype))goto _errout;
      
    }else{
      /* use dec_type 3: scalar offset into packed value array */

      s->dec_type=3;
      s->dec_nodeb=_determine_node_bytes(s->used_entries,_ilog(s->used_entries-1)/8+1); 
      s->dec_leafw=_determine_leaf_words(s->dec_nodeb,_ilog(s->used_entries-1)/8+1); 
      if(_make_decode_table(s,lengthlist,quantvals,opb,maptype))goto _errout;

      /* get the vals & pack them */
      s->q_pack=(s->q_bits+7)/8*s->dim;
      s->q_val=repair_alloc(s->q_pack*s->used_entries);
      if(!s->q_val) goto _eofout;

      if(s->q_bits<=8){
	for(i=0;i<s->used_entries*s->dim;i++)
	  ((unsigned char *)(s->q_val))[i]=tremor_oggpack_read(opb,s->q_bits);
      }else{
	for(i=0;i<s->used_entries*s->dim;i++)
	  ((ogg_uint16_t *)(s->q_val))[i]=tremor_oggpack_read(opb,s->q_bits);
      }
    }
    break;
  default:
    goto _errout;
  }

  if(tremor_oggpack_eop(opb))goto _eofout;

  media_lib_free(lengthlist);
  return 0;
 _errout:
 _eofout:
  media_lib_free(lengthlist);
  repair_vorbis_book_clear(s);
  return -1;
}

static void repair_floor0_free_info(vorbis_info_floor *i){
  vorbis_info_floor0 *info=(vorbis_info_floor0 *)i;
  if(info)media_lib_free(info);
}
vorbis_info_floor *repair_floor0_info_unpack (vorbis_info *vi,oggpack_buffer *opb){
  codec_setup_info     *ci=(codec_setup_info *)vi->codec_setup;
  int j;

  vorbis_info_floor0 *info=(vorbis_info_floor0 *)repair_alloc(sizeof(*info));
  if(!info)return NULL;
  info->order=tremor_oggpack_read(opb,8);
  info->rate=tremor_oggpack_read(opb,16);
  info->barkmap=tremor_oggpack_read(opb,16);
  info->ampbits=tremor_oggpack_read(opb,6);
  info->ampdB=tremor_oggpack_read(opb,8);
  info->numbooks=tremor_oggpack_read(opb,4)+1;
  
  if(info->order<1)goto err_out;
  if(info->rate<1)goto err_out;
  if(info->barkmap<1)goto err_out;
    
  for(j=0;j<info->numbooks;j++){
    info->books[j]=tremor_oggpack_read(opb,8);
    if(info->books[j]>=ci->books)goto err_out;
  }

  if(tremor_oggpack_eop(opb))goto err_out;
  return(info);

 err_out:
  repair_floor0_free_info(info);
  return(NULL);
}
static void repair_floor1_free_info(vorbis_info_floor *i){
  vorbis_info_floor1 *info=(vorbis_info_floor1 *)i;
  if(info){
    if(info->class)media_lib_free(info->class);
    if(info->partitionclass)media_lib_free(info->partitionclass);
    if(info->postlist)media_lib_free(info->postlist);
    if(info->forward_index)media_lib_free(info->forward_index);
    if(info->hineighbor)media_lib_free(info->hineighbor);
    if(info->loneighbor)media_lib_free(info->loneighbor);
    memset(info,0,sizeof(*info));
    media_lib_free(info);
  }
}
static int mergesort(char *index,ogg_uint16_t *vals,ogg_uint16_t n){
  ogg_uint16_t i,j;
  char *temp,*A=index,*B=repair_alloc(n*sizeof(*B));

  if(!B)return -1;
  for(i=1;i<n;i<<=1){
    for(j=0;j+i<n;){
      int k1=j;
      int mid=j+i;
      int k2=mid;
      int end=(j+i*2<n?j+i*2:n);
      while(k1<mid && k2<end){
	if(vals[(unsigned char)A[k1]]<vals[(unsigned char)A[k2]])
	  B[j++]=A[k1++];
	else
	  B[j++]=A[k2++];
      }
      while(k1<mid) B[j++]=A[k1++];
      while(k2<end) B[j++]=A[k2++];
    }
    for(;j<n;j++)B[j]=A[j];
    temp=A;A=B;B=temp;
  }
 
  if(B==index){
    for(j=0;j<n;j++)B[j]=A[j];
    media_lib_free(A);
  }else
    media_lib_free(B);
  return 0;
}
vorbis_info_floor *repair_floor1_info_unpack (vorbis_info *vi,oggpack_buffer *opb){
  codec_setup_info     *ci=(codec_setup_info *)vi->codec_setup;
  int j,k,count=0,maxclass=-1,rangebits;
  
  vorbis_info_floor1 *info=(vorbis_info_floor1 *)repair_calloc(1,sizeof(*info));
  if(!info)return NULL;
  /* read partitions */
  info->partitions=tremor_oggpack_read(opb,5); /* only 0 to 31 legal */
  if(info->partitions<0)goto err_out;
  info->partitionclass=
    (char *)repair_alloc(info->partitions*sizeof(*info->partitionclass));
  if(info->partitions && !info->partitionclass)goto err_out;
  for(j=0;j<info->partitions;j++){
    info->partitionclass[j]=tremor_oggpack_read(opb,4); /* only 0 to 15 legal */
    if(maxclass<info->partitionclass[j])maxclass=info->partitionclass[j];
  }

  /* read partition classes */
  info->class=
    (floor1class *)repair_alloc((maxclass+1)*sizeof(*info->class));
  if(maxclass>=0 && !info->class)goto err_out;
  for(j=0;j<maxclass+1;j++){
    info->class[j].class_dim=tremor_oggpack_read(opb,3)+1; /* 1 to 8 */
    info->class[j].class_subs=tremor_oggpack_read(opb,2); /* 0,1,2,3 bits */
    if(tremor_oggpack_eop(opb)<0) goto err_out;
    if(info->class[j].class_subs)
      info->class[j].class_book=tremor_oggpack_read(opb,8);
    else
      info->class[j].class_book=0;
    if(info->class[j].class_book>=ci->books)goto err_out;
    for(k=0;k<(1<<info->class[j].class_subs);k++){
      info->class[j].class_subbook[k]=tremor_oggpack_read(opb,8)-1;
      if(info->class[j].class_subbook[k]>=ci->books &&
	 info->class[j].class_subbook[k]!=0xff)goto err_out;
    }
  }

  /* read the post list */
  info->mult=tremor_oggpack_read(opb,2)+1;     /* only 1,2,3,4 legal now */ 
  rangebits=tremor_oggpack_read(opb,4);

  if(rangebits<0)goto err_out;
  for(j=0,k=0;j<info->partitions;j++)
    count+=info->class[(unsigned char)info->partitionclass[j]].class_dim; 
  info->postlist=
    (ogg_uint16_t *)repair_alloc((count+2)*sizeof(*info->postlist));
  info->forward_index=
    (char *)repair_alloc((count+2)*sizeof(*info->forward_index));
  info->loneighbor=
    (char *)repair_alloc(count*sizeof(*info->loneighbor));
  info->hineighbor=
    (char *)repair_alloc(count*sizeof(*info->hineighbor));

  if(!info->postlist || !info->forward_index ||
     (count && (!info->loneighbor || !info->hineighbor)))goto err_out;
  count=0;
  for(j=0,k=0;j<info->partitions;j++){
    count+=info->class[(unsigned char)info->partitionclass[j]].class_dim; 
    for(;k<count;k++){
      int t=info->postlist[k+2]=tremor_oggpack_read(opb,rangebits);
      if(t>=(1<<rangebits))goto err_out;
    }
  }
  if(tremor_oggpack_eop(opb))goto err_out;
  info->postlist[0]=0;
  info->postlist[1]=1<<rangebits;
  info->posts=count+2;

  /* also store a sorted position index */
  for(j=0;j<info->posts;j++)info->forward_index[j]=j;
  if(mergesort(info->forward_index,info->postlist,info->posts))goto err_out;
  
  /* discover our neighbors for decode where we don't use fit flags
     (that would push the neighbors outward) */
  for(j=0;j<info->posts-2;j++){
    int lo=0;
    int hi=1;
    int lx=0;
    int hx=info->postlist[1];
    int currentx=info->postlist[j+2];
    for(k=0;k<j+2;k++){
      int x=info->postlist[k];
      if(x>lx && x<currentx){
	lo=k;
	lx=x;
      }
      if(x<hx && x>currentx){
	hi=k;
	hx=x;
      }
    }
    info->loneighbor[j]=lo;
    info->hineighbor[j]=hi;
  }

  return(info);
  
 err_out:
  repair_floor1_free_info(info);
  return(NULL);
}
static void repair_res_clear_info(vorbis_info_residue *info){
  if(info){
    if(info->stagemasks)media_lib_free(info->stagemasks);
    if(info->stagebooks)media_lib_free(info->stagebooks);
    memset(info,0,sizeof(*info));
  }
}
static int repair_res_unpack(vorbis_info_residue *info,
		vorbis_info *vi,oggpack_buffer *opb){
  int j,k;
  codec_setup_info     *ci=(codec_setup_info *)vi->codec_setup;
  memset(info,0,sizeof(*info));

  info->type=tremor_oggpack_read(opb,16);
  if(info->type>2 || info->type<0)goto errout;
  info->begin=tremor_oggpack_read(opb,24);
  info->end=tremor_oggpack_read(opb,24);
  info->grouping=tremor_oggpack_read(opb,24)+1;
  info->partitions=tremor_oggpack_read(opb,6)+1;
  info->groupbook=tremor_oggpack_read(opb,8);
  if(info->groupbook>=ci->books)goto errout;

  info->stagemasks=repair_alloc(info->partitions*sizeof(*info->stagemasks));
  info->stagebooks=repair_alloc(info->partitions*8*sizeof(*info->stagebooks));

  if(!info->stagemasks || !info->stagebooks)goto errout;
  for(j=0;j<info->partitions;j++){
    int cascade=tremor_oggpack_read(opb,3);
    if(tremor_oggpack_read(opb,1))
      cascade|=(tremor_oggpack_read(opb,5)<<3);
    info->stagemasks[j]=cascade;
  }

  if(!info->stagemasks || !info->stagebooks)goto errout;
  for(j=0;j<info->partitions;j++){
    for(k=0;k<8;k++){
      if((info->stagemasks[j]>>k)&1){
	unsigned char book=tremor_oggpack_read(opb,8);
	if(book>=ci->books)goto errout;
	info->stagebooks[j*8+k]=book;
	if(k+1>info->stages)info->stages=k+1;
      }else
	info->stagebooks[j*8+k]=0xff;
    }
  }

  if(tremor_oggpack_eop(opb))goto errout;

  return 0;
 errout:
  repair_res_clear_info(info);
  return 1;
}
static void repair_mapping_clear_info(vorbis_info_mapping *info){
  if(info){
    if(info->chmuxlist)media_lib_free(info->chmuxlist);
    if(info->submaplist)media_lib_free(info->submaplist);
    if(info->coupling)media_lib_free(info->coupling);
    memset(info,0,sizeof(*info));
  }
}
static int ilog(unsigned int v){
  int ret=0;
  if(v)--v;
  while(v){
    ret++;
    v>>=1;
  }
  return(ret);
}
static int repair_mapping_info_unpack(vorbis_info_mapping *info,vorbis_info *vi,
			oggpack_buffer *opb){
  int i;
  codec_setup_info     *ci=(codec_setup_info *)vi->codec_setup;
  memset(info,0,sizeof(*info));

  if(tremor_oggpack_read(opb,1))
    info->submaps=tremor_oggpack_read(opb,4)+1;
  else
    info->submaps=1;

  if(tremor_oggpack_read(opb,1)){
    info->coupling_steps=tremor_oggpack_read(opb,8)+1;
    info->coupling=
      repair_alloc(info->coupling_steps*sizeof(*info->coupling));
    
    if(!info->coupling)goto err_out;
    for(i=0;i<info->coupling_steps;i++){
      int testM=info->coupling[i].mag=tremor_oggpack_read(opb,ilog(vi->channels));
      int testA=info->coupling[i].ang=tremor_oggpack_read(opb,ilog(vi->channels));

      if(testM<0 || 
	 testA<0 || 
	 testM==testA || 
	 testM>=vi->channels ||
	 testA>=vi->channels) goto err_out;
    }

  }

  if(tremor_oggpack_read(opb,2)>0)goto err_out; /* 2,3:reserved */
    
  if(info->submaps>1){
    info->chmuxlist=repair_alloc(sizeof(*info->chmuxlist)*vi->channels);
    if(!info->chmuxlist)goto err_out;
    for(i=0;i<vi->channels;i++){
      info->chmuxlist[i]=tremor_oggpack_read(opb,4);
      if(info->chmuxlist[i]>=info->submaps)goto err_out;
    }
  }

  info->submaplist=repair_alloc(sizeof(*info->submaplist)*info->submaps);
  if(!info->submaplist)goto err_out;
  for(i=0;i<info->submaps;i++){
    (void)tremor_oggpack_read(opb,8); // Reserved time configuration.
    info->submaplist[i].floor=tremor_oggpack_read(opb,8);
    if(info->submaplist[i].floor>=ci->floors)goto err_out;
    info->submaplist[i].residue=tremor_oggpack_read(opb,8);
    if(info->submaplist[i].residue>=ci->residues)goto err_out;
  }

  return 0;

 err_out:
  repair_mapping_clear_info(info);
  return -1;
}
static void repair_vorbis_info_clear(vorbis_info *vi){
  codec_setup_info     *ci=(codec_setup_info *)vi->codec_setup;
  int i;

  if(ci){

    if(ci->mode_param)media_lib_free(ci->mode_param);

    if(ci->map_param){
      for(i=0;i<ci->maps;i++) /* unpack does the range checking */
	repair_mapping_clear_info(ci->map_param+i);
      media_lib_free(ci->map_param);
    }

    if(ci->floor_param){
      for(i=0;i<ci->floors;i++) /* unpack does the range checking */
	if(ci->floor_type && ci->floor_type[i])
	  repair_floor1_free_info(ci->floor_param[i]);
	else
	  repair_floor0_free_info(ci->floor_param[i]);
      media_lib_free(ci->floor_param);
    }
    media_lib_free(ci->floor_type);

    if(ci->residue_param){
      for(i=0;i<ci->residues;i++) /* unpack does the range checking */
	repair_res_clear_info(ci->residue_param+i);
      media_lib_free(ci->residue_param);
    }

    if(ci->book_param){
      for(i=0;i<ci->books;i++)
	repair_vorbis_book_clear(ci->book_param+i);
      media_lib_free(ci->book_param);
    }
    
    media_lib_free(ci);
  }

  memset(vi,0,sizeof(*vi));
}
static int repair__vorbis_unpack_info(vorbis_info *vi,oggpack_buffer *opb){
  codec_setup_info     *ci=(codec_setup_info *)vi->codec_setup;
  if(!ci)return(OV_EFAULT);

  vi->version=tremor_oggpack_read(opb,32);
  if(vi->version!=0)return(OV_EVERSION);

  vi->channels=tremor_oggpack_read(opb,8);
  vi->rate=tremor_oggpack_read(opb,32);

  vi->bitrate_upper=tremor_oggpack_read(opb,32);
  vi->bitrate_nominal=tremor_oggpack_read(opb,32);
  vi->bitrate_lower=tremor_oggpack_read(opb,32);

  int short_bits=tremor_oggpack_read(opb,4), long_bits=tremor_oggpack_read(opb,4);
  if(short_bits<0 || long_bits<0)goto err_out;
  ci->blocksizes[0]=1<<short_bits;
  ci->blocksizes[1]=1<<long_bits;
  
#ifdef LIMIT_TO_64kHz
  if(vi->rate>=64000 || ci->blocksizes[1]>4096)goto err_out;
#else
  if(vi->rate<64000 && ci->blocksizes[1]>4096)goto err_out;
#endif

  if(vi->rate<1)goto err_out;
  if(vi->channels<1)goto err_out;
  if(ci->blocksizes[0]<64)goto err_out; 
  if(ci->blocksizes[1]<ci->blocksizes[0])goto err_out;
  if(ci->blocksizes[1]>8192)goto err_out;
  
  if(tremor_oggpack_read(opb,1)!=1)goto err_out; /* EOP check */

  return(0);
 err_out:
  repair_vorbis_info_clear(vi);
  return(OV_EBADHEADER);
}

static void repair_dsp_destroy(vorbis_dsp_state *dsp) {
    if (!dsp) return;
    for (int channel = 0; channel < dsp->vi->channels; ++channel) {
        if (dsp->work) media_lib_free(dsp->work[channel]);
        if (dsp->mdctright) media_lib_free(dsp->mdctright[channel]);
    }
    media_lib_free(dsp->work);
    media_lib_free(dsp->mdctright);
    media_lib_free(dsp);
}

static vorbis_dsp_state *repair_dsp_create(vorbis_info *info) {
    vorbis_dsp_state *dsp = repair_alloc(sizeof(*dsp));
    if (!dsp) return NULL;
    dsp->vi = info;
    dsp->work = repair_calloc(info->channels, sizeof(*dsp->work));
    dsp->mdctright = repair_calloc(info->channels, sizeof(*dsp->mdctright));
    if (!dsp->work || !dsp->mdctright) goto failed;
    for (int channel = 0; channel < info->channels; ++channel) {
        size_t long_block = info->codec_setup->blocksizes[1];
        dsp->work[channel] = repair_calloc(long_block / 2, sizeof(int32_t));
        dsp->mdctright[channel] = repair_calloc(long_block / 4, sizeof(int32_t));
        if (!dsp->work[channel] || !dsp->mdctright[channel]) goto failed;
    }
    dsp->out_begin = dsp->out_end = -1;
    dsp->granulepos = dsp->sequence = dsp->sample_count = -1;
    return dsp;
failed:
    repair_dsp_destroy(dsp);
    return NULL;
}

static int repair_header(vorbis_info *info, uint8_t *data, size_t size,
                         int (*unpack)(vorbis_info *, oggpack_buffer *)) {
    ogg_buffer buffer = {.data = data, .size = size};
    ogg_reference reference = {.buffer = &buffer, .length = size};
    oggpack_buffer bits = {.headptr = data, .headend = size, .head = &reference};
    return unpack(info, &bits);
}

esp_audio_err_t __wrap_esp_vorbis_dec_open(void *configuration, uint32_t bytes,
                                         void **handle) {
    if (!handle) return ESP_AUDIO_ERR_INVALID_PARAMETER;
    *handle = NULL;
    if (!configuration || bytes != sizeof(esp_vorbis_dec_cfg_t))
        return ESP_AUDIO_ERR_INVALID_PARAMETER;
    esp_vorbis_dec_cfg_t *cfg = configuration;
    if (!cfg->info_header || !cfg->info_size || !cfg->setup_header || !cfg->setup_size)
        return ESP_AUDIO_ERR_INVALID_PARAMETER;
    esp_audio_err_t result = ESP_AUDIO_ERR_MEM_LACK;
    vorbis_wrapper *wrapper = repair_alloc(sizeof(*wrapper));
    vorbis_info *info = NULL;
    if (!wrapper) return result;
    info = repair_alloc(sizeof(*info));
    if (!info) goto failed;
    info->codec_setup = repair_alloc(sizeof(*info->codec_setup));
    if (!info->codec_setup) goto failed;
    if (repair_header(info, cfg->info_header, cfg->info_size, repair__vorbis_unpack_info) ||
        repair_header(info, cfg->setup_header, cfg->setup_size, repair__vorbis_unpack_books)) {
        result = ESP_AUDIO_ERR_FAIL;
        goto failed;
    }
    wrapper->dsp = repair_dsp_create(info);
    if (!wrapper->dsp) goto failed;
    *handle = wrapper;
    return ESP_AUDIO_ERR_OK;
failed:
    if (info) {
        repair_vorbis_info_clear(info);
        media_lib_free(info);
    }
    media_lib_free(wrapper);
    return result;
}

esp_audio_err_t __wrap_esp_vorbis_dec_register(void) {
    static const esp_audio_dec_ops_t operations = {
        .open = __wrap_esp_vorbis_dec_open,
        .decode = esp_vorbis_dec_decode,
        .reset = esp_vorbis_dec_reset,
        .close = esp_vorbis_dec_close,
    };
    return esp_audio_dec_register(ESP_AUDIO_TYPE_VORBIS, &operations);
}
static int repair__vorbis_unpack_books(vorbis_info *vi,oggpack_buffer *opb){
  codec_setup_info     *ci=(codec_setup_info *)vi->codec_setup;
  int i;
  if(!ci)return(OV_EFAULT);

  /* codebooks */
  ci->books=tremor_oggpack_read(opb,8)+1;
  ci->book_param=(codebook *)repair_calloc(ci->books,sizeof(*ci->book_param));
  if(!ci->book_param)goto err_out;
  for(i=0;i<ci->books;i++)
    if(repair_vorbis_book_unpack(opb,ci->book_param+i))goto err_out;

  /* time backend settings, not actually used */
  i=tremor_oggpack_read(opb,6);
  for(;i>=0;i--)
    if(tremor_oggpack_read(opb,16)!=0)goto err_out;

  /* floor backend settings */
  ci->floors=tremor_oggpack_read(opb,6)+1;
  ci->floor_param=repair_alloc(sizeof(*ci->floor_param)*ci->floors);
  ci->floor_type=repair_alloc(sizeof(*ci->floor_type)*ci->floors);
  if(!ci->floor_param || !ci->floor_type)goto err_out;
  for(i=0;i<ci->floors;i++){
    int floor_type=tremor_oggpack_read(opb,16);
    if(floor_type<0 || floor_type>=VI_FLOORB)goto err_out;
    ci->floor_type[i]=floor_type;
    if(ci->floor_type && ci->floor_type[i])
      ci->floor_param[i]=repair_floor1_info_unpack(vi,opb);
    else
      ci->floor_param[i]=repair_floor0_info_unpack(vi,opb);
    if(!ci->floor_param[i])goto err_out;
  }

  /* residue backend settings */
  ci->residues=tremor_oggpack_read(opb,6)+1;
  ci->residue_param=repair_alloc(sizeof(*ci->residue_param)*ci->residues);
  if(!ci->residue_param)goto err_out;
  for(i=0;i<ci->residues;i++)
    if(repair_res_unpack(ci->residue_param+i,vi,opb))goto err_out;

  /* map backend settings */
  ci->maps=tremor_oggpack_read(opb,6)+1;
  ci->map_param=repair_alloc(sizeof(*ci->map_param)*ci->maps);
  if(!ci->map_param)goto err_out;
  for(i=0;i<ci->maps;i++){
    if(tremor_oggpack_read(opb,16)!=0)goto err_out;
    if(repair_mapping_info_unpack(ci->map_param+i,vi,opb))goto err_out;
  }
  
  /* mode settings */
  ci->modes=tremor_oggpack_read(opb,6)+1;
  ci->mode_param=
    (vorbis_info_mode *)repair_alloc(ci->modes*sizeof(*ci->mode_param));
  if(!ci->mode_param)goto err_out;
  for(i=0;i<ci->modes;i++){
    ci->mode_param[i].blockflag=tremor_oggpack_read(opb,1);
    if(tremor_oggpack_read(opb,16))goto err_out;
    if(tremor_oggpack_read(opb,16))goto err_out;
    ci->mode_param[i].mapping=tremor_oggpack_read(opb,8);
    if(ci->mode_param[i].mapping>=ci->maps)goto err_out;
  }
  
  if(tremor_oggpack_read(opb,1)!=1)goto err_out; /* top level EOP check */

  return(0);
 err_out:
  repair_vorbis_info_clear(vi);
  return(OV_EBADHEADER);
}
