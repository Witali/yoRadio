long oggpackB_read(oggpack_buffer *b,int bits){
  long ret;
  long m=32-bits;

  if(m<0 || m>32) goto err;
  bits+=b->endbit;

  if(b->endbyte+4>=b->storage){
    /* not the main path */
    if(b->endbyte > b->storage-((bits+7)>>3)) goto overflow;
    /* special case to avoid reading b->ptr[0], which might be past the end of
        the buffer; also skips some useless accounting */
    else if(!bits)return(0L);
  }

  ret=(unsigned long)b->ptr[0]<<(24+b->endbit);
  if(bits>8){
    ret|=(unsigned long)b->ptr[1]<<(16+b->endbit);
    if(bits>16){
      ret|=(unsigned long)b->ptr[2]<<(8+b->endbit);
      if(bits>24){
        ret|=(unsigned long)b->ptr[3]<<(b->endbit);
        if(bits>32 && b->endbit)
          ret|=b->ptr[4]>>(8-b->endbit);
      }
    }
  }
  ret=((ret&0xffffffffUL)>>(m>>1))>>((m+1)>>1);

  b->ptr+=bits/8;
  b->endbyte+=bits/8;
  b->endbit=bits&7;
  return ret;

 overflow:
 err:
  b->ptr=NULL;
  b->endbyte=b->storage;
  b->endbit=1;
  return -1L;
}
