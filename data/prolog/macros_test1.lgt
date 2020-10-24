:- set_logtalk_flag(clean, on), set_logtalk_flag(debug, on), logtalk_load(my_macros), logtalk_load(listp, [hook(my_macros)]), logtalk_load(source, [hook(my_macros)]).
