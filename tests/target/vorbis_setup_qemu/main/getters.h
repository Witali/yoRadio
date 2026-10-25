// Verbatim actual public-getter capture helper; no oracle/golden decisions.
static void getter_append(uint32_t *out,size_t capacity,size_t *count,uint32_t value){assert(*count<capacity);out[(*count)++]=value;}
static size_t capture_getters(const native_vorbis_setup_t *setup,uint32_t *out,size_t capacity){
    size_t n=0;
#define EMIT(value) getter_append(out,capacity,&n,(value))
#define ARRAY(values,count) do{for(size_t j_=0;j_<(size_t)(count);j_++){EMIT((values)[j_]);}}while(0)
    for(uint32_t i=0;i<setup->layout.floor_count;i++){
        uint32_t type=99;assert(native_vorbis_setup_floor_type(setup,i,&type)==0);EMIT(type);
        if(type==0){native_vorbis_floor0_setup_t f;assert(native_vorbis_setup_floor0(setup,i,&f)==0);
            EMIT(f.order);EMIT(f.rate);EMIT(f.bark_map_size);EMIT(f.amplitude_bits);EMIT(f.amplitude_offset);EMIT(f.book_count);ARRAY(f.books,f.book_count);
        }else{assert(type==1);native_vorbis_floor1_setup_t f;assert(native_vorbis_setup_floor1(setup,i,&f)==0);
            EMIT(f.partition_count);EMIT(f.class_count);EMIT(f.multiplier);EMIT(f.range_bits);EMIT(f.post_count);
            ARRAY(f.partitions,f.partition_count);ARRAY(f.class_offsets,f.class_count);ARRAY(f.x,f.post_count);
            for(uint32_t c=0;c<f.class_count;c++){native_vorbis_floor1_class_t cls;assert(native_vorbis_setup_floor1_class(setup,&f,c,&cls)==0);
                EMIT(cls.dimensions);EMIT(cls.subclass_bits);EMIT(cls.masterbook);EMIT(cls.book_count);ARRAY(cls.books,cls.book_count);}
        }
    }
    for(uint32_t i=0;i<setup->layout.residue_count;i++){native_vorbis_residue_setup_t r;assert(native_vorbis_setup_residue(setup,i,&r)==0);
        EMIT(r.type);EMIT(r.begin);EMIT(r.end);EMIT(r.partition_size);EMIT(r.classifications);EMIT(r.classbook);EMIT(r.stage_book_count);
        ARRAY(r.cascades,r.classifications);ARRAY(r.book_offsets,r.classifications);ARRAY(r.books,r.stage_book_count);}
    for(uint32_t i=0;i<setup->layout.mapping_count;i++){native_vorbis_mapping_setup_t m;assert(native_vorbis_setup_mapping(setup,i,&m)==0);
        EMIT(m.submap_count);EMIT(m.coupling_count);EMIT(m.channels);ARRAY(m.coupling_pairs,2*m.coupling_count);ARRAY(m.mux,m.channels);ARRAY(m.submaps,3*m.submap_count);}
    for(uint32_t i=0;i<setup->layout.mode_count;i++){native_vorbis_mode_setup_t m;assert(native_vorbis_setup_mode(setup,i,&m)==0);EMIT(m.blockflag);EMIT(m.mapping);}
#undef ARRAY
#undef EMIT
    return n;
}
