void vorbis_comment_add(vorbis_comment *vc,const char *comment){
  vc->user_comments=_ogg_realloc(vc->user_comments,
                            (vc->comments+2)*sizeof(*vc->user_comments));
  vc->comment_lengths=_ogg_realloc(vc->comment_lengths,
                                  (vc->comments+2)*sizeof(*vc->comment_lengths));
  vc->comment_lengths[vc->comments]=strlen(comment);
  vc->user_comments[vc->comments]=_ogg_malloc(vc->comment_lengths[vc->comments]+1);
  strcpy(vc->user_comments[vc->comments], comment);
  vc->comments++;
  vc->user_comments[vc->comments]=NULL;
}

void vorbis_comment_add_tag(vorbis_comment *vc, const char *tag, const char *contents){
  /* Length for key and value +2 for = and \0 */
  char *comment=_ogg_malloc(strlen(tag)+strlen(contents)+2);
  strcpy(comment, tag);
  strcat(comment, "=");
  strcat(comment, contents);
  vorbis_comment_add(vc, comment);
  _ogg_free(comment);
}

/* This is more or less the same as strncasecmp - but that doesn't exist
 * everywhere, and this is a fairly trivial function, so we include it */
static int tagcompare(const char *s1, const char *s2, int n){
  int c=0;
  while(c < n){
    if(_v_toupper(s1[c]) != _v_toupper(s2[c]))
      return !0;
    c++;
  }
  return 0;
}

char *vorbis_comment_query(vorbis_comment *vc, const char *tag, int count){
  long i;
  int found = 0;
  int taglen = strlen(tag)+1; /* +1 for the = we append */
  char *fulltag = _ogg_malloc(taglen+1);

  strcpy(fulltag, tag);
  strcat(fulltag, "=");

  for(i=0;i<vc->comments;i++){
    if(!tagcompare(vc->user_comments[i], fulltag, taglen)){
      if(count == found) {
        /* We return a pointer to the data, not a copy */
        _ogg_free(fulltag);
        return vc->user_comments[i] + taglen;
      } else {
        found++;
      }
    }
  }
  _ogg_free(fulltag);
  return NULL; /* didn't find anything */
}

int vorbis_comment_query_count(vorbis_comment *vc, const char *tag){
  int i,count=0;
  int taglen = strlen(tag)+1; /* +1 for the = we append */
  char *fulltag = _ogg_malloc(taglen+1);
  strcpy(fulltag,tag);
  strcat(fulltag, "=");

  for(i=0;i<vc->comments;i++){
    if(!tagcompare(vc->user_comments[i], fulltag, taglen))
      count++;
  }

  _ogg_free(fulltag);
  return count;
}
