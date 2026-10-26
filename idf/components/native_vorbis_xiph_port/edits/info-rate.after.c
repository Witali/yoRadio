  vi->channels=oggpack_read(opb,8);
  {
    /* Two checked pieces keep valid 0xffffffff distinct from EOP on ILP32. */
    long low=oggpack_read(opb,16);
    long high=oggpack_read(opb,16);
    if(low<0 || high<0)goto err_out;
    vi->rate=((unsigned long)high<<16)|(unsigned long)low;
  }
