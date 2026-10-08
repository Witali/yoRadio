"""Generate a project-local esp-lwIP TCP fix; never modify the shared SDK.

Audited against the exact IDF 6.0.2 and 6.0.3 sources below.
A SHUT_WR netconn can still own a TIME_WAIT PCB. Both reclamation paths must
notify that owner before the storage is reused. Normal tcp_close callers have
TF_RXCLOSED and have already relinquished ownership.
"""
import argparse
import hashlib
from pathlib import Path

SOURCE_SHA256 = 'add731715c74fbcb50f85ce504e32168f93dd66c0d4f8aa42d355227f53fe59d'
API_SOURCE_SHA256 = 'a793b371032ba38ca5e23fd7fede4c910aea0079ffe612d781109f203eab92a0'
# IDF 6.0.3 (esp-lwIP c6f2f878): only DNS result-count handling changed
# in api_msg.c. The close/shutdown ownership paths and tcp.c are unchanged.
API_SOURCE_SHA256_IDF_603 = 'ac3c486b362318ea265e8b8c07cf74fe571fe4197415fbd7de5b74390f9019ff'


def patch(source):
    if hashlib.sha256(source.encode()).hexdigest() != SOURCE_SHA256:
        raise ValueError('Unaudited lwIP tcp.c: revalidate TIME_WAIT fix against this SDK')
    helper = '''/** Release a detached TIME_WAIT PCB, notifying a half-close owner. */
static void
tcp_free_timewait(struct tcp_pcb *pcb)
{
  u8_t notify = (pcb->flags & TF_RXCLOSED) == 0;
#if LWIP_CALLBACK_API
  tcp_err_fn err_fn = pcb->errf;
#endif
  void *err_arg = pcb->callback_arg;
  tcp_free(pcb);
  if (notify) {
    /* Like tcp_input_delayed_close: no PCB remains, but queued receive data
       and EOF still belong to the netconn. Do not report a connection reset. */
    TCP_EVENT_ERR(TIME_WAIT, err_fn, err_arg, ERR_CLSD);
  }
}

'''
    replacements = [
        ('/** Free a tcp listen pcb */', helper + '/** Free a tcp listen pcb */'),
        ('''    tcp_pcb_remove(&tcp_tw_pcbs, pcb);
    tcp_free(pcb);''', '''    tcp_pcb_remove(&tcp_tw_pcbs, pcb);
    tcp_free_timewait(pcb);'''),
        ('''      pcb2 = pcb;
      pcb = pcb->next;
      tcp_free(pcb2);
    } else {
      prev = pcb;
      pcb = pcb->next;
    }
  }
}''', '''      pcb2 = pcb;
      tcp_free_timewait(pcb2);
      /* The error callback may close or allocate other PCBs. Restart from
         the current list head, never a pointer retained across the callback. */
      prev = NULL;
      pcb = tcp_tw_pcbs;
    } else {
      prev = pcb;
      pcb = pcb->next;
    }
  }
}'''),
    ]
    for before, after in replacements:
        if source.count(before) != 1:
            raise ValueError('TIME_WAIT patch context is not unique')
        source = source.replace(before, after)
    return source


def patch_api(source):
    if hashlib.sha256(source.encode()).hexdigest() not in (
            API_SOURCE_SHA256, API_SOURCE_SHA256_IDF_603):
        raise ValueError('Unaudited lwIP api_msg.c: revalidate half-close ownership fix')
    before = '''              (tpcb->state == CLOSING))) {'''
    after = '''              (tpcb->state == CLOSING) ||
              (tpcb->state == LAST_ACK) ||
              (tpcb->state == TIME_WAIT))) {'''
    if source.count(before) != 1:
        raise ValueError('Half-close patch context is not unique')
    return source.replace(before, after)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--kind', choices=('tcp', 'api'), default='tcp')
    args = parser.parse_args()
    result = (patch if args.kind == 'tcp' else patch_api)(args.input.read_text())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not args.output.exists() or args.output.read_text() != result:
        args.output.write_text(result, newline='\n')
