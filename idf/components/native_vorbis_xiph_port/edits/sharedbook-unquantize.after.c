float *_book_unquantize(const static_codebook *b,int n,int *sparsemap){
  long j,k,count=0;
  if(b->maptype==1 || b->maptype==2){
    int quantvals;
    float mindel=_float32_unpack(b->q_min);
    float delta=_float32_unpack(b->q_delta);
    float *r;
    if(n<0 || b->dim<0 ||
       (b->dim && (size_t)n>((size_t)-1)/sizeof(*r)/(size_t)b->dim))
      return(NULL);
    r=_ogg_calloc((size_t)n*(size_t)b->dim,sizeof(*r));
    if(r==NULL)return(NULL);
