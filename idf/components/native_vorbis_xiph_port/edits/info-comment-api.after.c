#include <limits.h>
#include <stdint.h>
#include "native_vorbis_xiph_comment_error.h"

/* Allocate a complete replacement before publishing any comment state.
   Existing strings stay owned and keep their addresses, including bytes
   after an embedded NUL in a parsed length-delimited comment. */
static int comment_insert(vorbis_comment *vc,const char *prefix,size_t prefixlen,
                          const char *value,size_t valuelen,int tagged){
  size_t count,length,slots;
  char **comments;
  int *lengths;
  char *copy;
  size_t separator=tagged?1U:0U;

  if(!vc || !prefix || (tagged && !value) ||
     vc->comments<0 || vc->comments==INT_MAX)return(OV_EINVAL);
  count=(size_t)vc->comments;
  if(count && (!vc->user_comments || !vc->comment_lengths))return(OV_EINVAL);
  if(prefixlen>(size_t)INT_MAX-separator ||
     valuelen>(size_t)INT_MAX-separator-prefixlen)return(OV_EINVAL);
  length=prefixlen+separator+valuelen;
  if(count>SIZE_MAX-2)return(OV_EINVAL);
  slots=count+2;
  if(slots>SIZE_MAX/sizeof(*comments) ||
     slots>SIZE_MAX/sizeof(*lengths) || length==SIZE_MAX)return(OV_EINVAL);

  comments=_ogg_malloc(slots*sizeof(*comments));
  if(!comments)return(OV_EFAULT);
  lengths=_ogg_malloc(slots*sizeof(*lengths));
  if(!lengths){_ogg_free(comments);return(OV_EFAULT);}
  copy=_ogg_malloc(length+1);
  if(!copy){_ogg_free(lengths);_ogg_free(comments);return(OV_EFAULT);}

  if(count){
    memcpy(comments,vc->user_comments,count*sizeof(*comments));
    memcpy(lengths,vc->comment_lengths,count*sizeof(*lengths));
  }
  memcpy(copy,prefix,prefixlen);
  if(tagged){
    copy[prefixlen]='=';
    memcpy(copy+prefixlen+1,value,valuelen);
  }
  copy[length]='\0';
  comments[count]=copy;
  comments[count+1]=NULL;
  lengths[count]=(int)length;
  lengths[count+1]=0;
  _ogg_free(vc->user_comments);
  _ogg_free(vc->comment_lengths);
  vc->user_comments=comments;
  vc->comment_lengths=lengths;
  vc->comments++;
  return(0);
}

int native_xiph_comment_add(vorbis_comment *vc,const char *comment){
  if(!comment)return(OV_EINVAL);
  return(comment_insert(vc,comment,strlen(comment),NULL,0,0));
}

int native_xiph_comment_add_tag(vorbis_comment *vc,const char *tag,const char *contents){
  if(!tag || !contents)return(OV_EINVAL);
  return(comment_insert(vc,tag,strlen(tag),contents,strlen(contents),1));
}

void vorbis_comment_add(vorbis_comment *vc,const char *comment){
  (void)native_xiph_comment_add(vc,comment);
}

void vorbis_comment_add_tag(vorbis_comment *vc,const char *tag,const char *contents){
  (void)native_xiph_comment_add_tag(vc,tag,contents);
}

static int comment_matches_tag(const char *comment,const char *tag,size_t length){
  size_t i;
  if(!comment)return(0);
  for(i=0;i<length;i++){
    if(!comment[i] ||
       _v_toupper((unsigned char)comment[i])!=_v_toupper((unsigned char)tag[i]))
      return(0);
  }
  return(comment[length]=='=');
}

char *vorbis_comment_query(vorbis_comment *vc,const char *tag,int count){
  int i,found=0;
  size_t length;
  if(!vc || !tag || count<0 || vc->comments<=0 || !vc->user_comments)return(NULL);
  length=strlen(tag);
  for(i=0;i<vc->comments;i++){
    if(comment_matches_tag(vc->user_comments[i],tag,length)){
      if(count==found)return(vc->user_comments[i]+length+1);
      found++;
    }
  }
  return(NULL);
}

int vorbis_comment_query_count(vorbis_comment *vc,const char *tag){
  int i,count=0;
  size_t length;
  if(!vc || !tag || vc->comments<=0 || !vc->user_comments)return(0);
  length=strlen(tag);
  for(i=0;i<vc->comments;i++)
    if(comment_matches_tag(vc->user_comments[i],tag,length))count++;
  return(count);
}
