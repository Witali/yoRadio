# Keep the authenticated hot SILK/CELT ASM corpus. The frozen packet dispatcher
# predates the optional per-coded-frame PCM lease API; compile ONLY that existing
# C unit with the lease define. No decoder state ABI or arithmetic is changed.
function(yoradio_opus_pcm_lease_dispatcher output component)
  set(selected "")
  set(replaced 0)
  foreach(src IN LISTS ARGN)
    if(src MATCHES "/upstream/src/opus_decoder[.]c[.]s$")
      list(APPEND selected "${component}/upstream/src/opus_decoder.c")
      math(EXPR replaced "${replaced}+1")
    else()
      list(APPEND selected "${src}")
    endif()
  endforeach()
  if(NOT replaced EQUAL 1)
    message(FATAL_ERROR "PCM leases require exactly one frozen packet dispatcher")
  endif()
  set(${output} "${selected}" PARENT_SCOPE)
endfunction()
