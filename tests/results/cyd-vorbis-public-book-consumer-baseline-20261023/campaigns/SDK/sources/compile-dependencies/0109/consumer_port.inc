static inline ogg_uint32_t decode_packed_entry_number(codebook *book, 
						      oggpack_buffer *b){
  ogg_uint32_t chase=0;
  int  read=book->dec_maxlength;
  long lok = oggpack_look(b,read),i;
  
  while(lok<0 && read>1)
    lok = oggpack_look(b, --read);

  if(lok<0){
    oggpack_adv(b,1); /* force eop */
    return -1;
  }

  /* chase the tree with the bits we got */
  if(book->dec_nodeb==1){
    if(book->dec_leafw==1){

      /* 8/8 */
      unsigned char *t=(unsigned char *)book->dec_table;
      for(i=0;i<read;i++){
	chase=t[chase*2+((lok>>i)&1)];
	if(chase&0x80UL)break;
      }
      chase&=0x7fUL;

    }else{

      /* 8/16 */
      unsigned char *t=(unsigned char *)book->dec_table;
      for(i=0;i<read;i++){
	int bit=(lok>>i)&1;
	int next=t[chase+bit];
	if(next&0x80){
	  chase= (next<<8) | t[chase+bit+1+(!bit || t[chase]&0x80)];
	  break;
	}
	chase=next;
      }
      chase&=0x7fffUL;
    }

  }else{
    if(book->dec_nodeb==2){
      if(book->dec_leafw==1){
	
	/* 16/16 */
	for(i=0;i<read;i++){
	  chase=((ogg_uint16_t *)(book->dec_table))[chase*2+((lok>>i)&1)];
	  if(chase&0x8000UL)break;
	}
	chase&=0x7fffUL;
	
      }else{
	
	/* 16/32 */
	ogg_uint16_t *t=(ogg_uint16_t *)book->dec_table;
	for(i=0;i<read;i++){
	  int bit=(lok>>i)&1;
	  int next=t[chase+bit];
	  if(next&0x8000){
	    chase= (next<<16) | t[chase+bit+1+(!bit || t[chase]&0x8000)];
	    break;
	  }
	  chase=next;
	}
	chase&=0x7fffffffUL;
      }
      
    }else{
      
      for(i=0;i<read;i++){
	chase=((ogg_uint32_t *)(book->dec_table))[chase*2+((lok>>i)&1)];
	if(chase&0x80000000UL)break;
      }
      chase&=0x7fffffffUL;
      
    }
  }
  
  if(i<read){
    oggpack_adv(b,i+1);
    return chase;
  }
  oggpack_adv(b,read+1);
  return(-1);
}

static int public_decode_map(codebook *s, oggpack_buffer *b, ogg_int32_t *v, int point){
  ogg_uint32_t entry = decode_packed_entry_number(s,b);
  int i;
  if(oggpack_eop(b))return(-1);

  /* according to decode type */
  switch(s->dec_type){
  case 1:{
    /* packed vector of values */
    int mask=(1<<s->q_bits)-1;
    for(i=0;i<s->dim;i++){
      v[i]=entry&mask;
      entry>>=s->q_bits;
    }
    break;
  }
  case 2:{
    /* packed vector of column offsets */
    int mask=(1<<s->q_pack)-1;
    for(i=0;i<s->dim;i++){
      if(s->q_bits<=8)
	v[i]=((unsigned char *)(s->q_val))[entry&mask];
      else
	v[i]=((ogg_uint16_t *)(s->q_val))[entry&mask];
      entry>>=s->q_pack;
    }
    break;
  }
  case 3:{
    /* offset into array */
    void *ptr=(unsigned char *)s->q_val+entry*s->q_pack;

    if(s->q_bits<=8){
      for(i=0;i<s->dim;i++)
	v[i]=((unsigned char *)ptr)[i];
    }else{
      for(i=0;i<s->dim;i++)
	v[i]=((ogg_uint16_t *)ptr)[i];
    }
    break;
  }
  default:
    return -1;
  }

  /* we have the unpacked multiplicands; compute final vals */
  {
    int shiftM=point-s->q_delp;
    ogg_int32_t add=point-s->q_minp;
    if(add>0)
      add= s->q_min >> add;
    else
      add= s->q_min << -add;

    if(shiftM>0)
      for(i=0;i<s->dim;i++)
	v[i]= add + ((v[i] * s->q_del) >> shiftM);
    else
      for(i=0;i<s->dim;i++)
	v[i]= add + ((v[i] * s->q_del) << -shiftM);

    if(s->q_seq)
      for(i=1;i<s->dim;i++)
	v[i]+=v[i-1];
  }

  return 0;
}

