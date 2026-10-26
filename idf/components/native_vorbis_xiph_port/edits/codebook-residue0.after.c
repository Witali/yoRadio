long vorbis_book_decodevs_add(codebook *book,float *a,oggpack_buffer *b,int n){
  if(book->used_entries>0){
    int step=n/book->dim;
    int i,j;

    /* Vorbis I 8.6.3: publish each complete vector before the next read.
       Distinct destinations need no partition-sized entry/pointer scratch.
       On EOP the completed word prefix remains, as required by 8.6.2. */
    for(j=0;j<step;j++){
      long entry=decode_packed_entry_number(book,b);
      const float *t;
      if(entry==-1)return(-1);
      t=book->valuelist+entry*book->dim;
      for(i=0;i<book->dim;i++)
        a[j+i*step]+=t[i];
    }
  }
  return(0);
}

