ogg_uint32_t *_make_words(char *l,long n,long sparsecount){
  long i,j,count=0;
  ogg_uint32_t marker[33];
  ogg_uint32_t *r;
  size_t words;
  if(n<0 || sparsecount<0 || sparsecount>n)return(NULL);
  words=(size_t)(sparsecount?sparsecount:n);
  if(words>((size_t)-1)/sizeof(*r))return(NULL);
  r=_ogg_malloc(words*sizeof(*r));
  if(r==NULL)return(NULL);
  memset(marker,0,sizeof(marker));
