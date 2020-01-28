:- use_module(library(dcg/basics)).


%x(Currency) --> integer(_).
%gb_currency_from_fn(Currency) --> [integer(_), white, string_without(" ", Currency), remainder(_)].
%Devisen Spot AUD 20'000.00 at 1.431200


gbtd('Expenses') --> [`Verfall Terming. `].
%Devisen Spot AUD 20'000.00 at 1.431200
gbtd('Transfers') --> "Devisen Spot", remainder(_).
gbtd('Expenses') --> "Vergütung Cornercard".
gbtd2(desc(Verb,[])) --> gbtd(Verb).
gbtd2(desc('Invest_In', [coord(Unit, Count)])) --> "Zeichnung ", gb_number(Count), " ", remainder(Codes), {atom_codes(Unit, Codes)}.

gb_number(X) --> gb_number_chars(Y), {phrase(number(X), Y)}.
gb_number_chars([H|T]) --> digit(H), gb_number_chars(T).
gb_number_chars([0'.|T]) --> ".", gb_number_chars(T).
gb_number_chars(T) --> "'", gb_number_chars(T).
gb_number_chars([]) --> [].



gb_date(date(M, D)) --> (D), ".", number(M).

