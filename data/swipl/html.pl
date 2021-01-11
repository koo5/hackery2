:- use_module(library(http/html_write)).
:- use_module(library(memfile)).

:- atom_to_memory_file('<html><head></head><body></body></html>', Memfile),
    open_memory_file(Memfile, read, Stream),
/*  open_hash_stream(In0, In, [algorithm(sha256)]), */
    load_html(Stream, DOM, []),
    close(Stream),
    writeln(DOM),
    print_html(DOM).
    
