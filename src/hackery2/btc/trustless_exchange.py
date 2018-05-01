#!/usr/bin/env python2
# coding: utf-8

#requirements: pip install --user python-jsonrpc click

import pyjsonrpc
import click

c = pyjsonrpc.HttpClient(
    url = "http://localhost:18332/",
    username = "a123",
    password = "a123"
)

@click.command()
@click.argument('my_pubkey')
@click.argument('their_pubkey')
@click.argument('my_address')
@click.argument('their_address')
@click.argument('their_refund_tx_hex')
@click.argument('their_refund_tx_id')

def main(my_pubkey, their_pubkey, my_address, their_address, their_refund_tx_hex, their_refund_tx_id):
	c.importpubkey(their_pubkey)
	multisig_address = c.addmultisigaddress(their_address, my_address)
	multisig_address_info = c.validateaddress(multisig_address.address)

	#my_priv_key = c.dumpprivkey(my_pub_

	my_raw_sending_transaction = x.createrawtransaction({\"txid\":\"3049177f4ec2fae44e220e2f7b48084409beae0bf1fd5c1a9bd2a999b9eb70ae\",\"vout\":0\}\],
		 {"2NBBSexjUfwby3oqvfeSNPWeYmqDagNNPUe\":amount_sent}

	my_raw_refund_tx = x.createrawtransaction(..
	
	c.signrawtransaction(their_refund_tx_hex, [
		{
			"txid":
			,"vout":0,
			"scriptPubKey":
			,"redeemScript":,
			"amount":their_btc_amount
		}
		,{
			"txid":
			,"vout":0,
			"scriptPubKey":,
			"redeemScript":,
			"amount":my_btc_amount
		}],
		[my_private_key]
	)

	print("done")

if __name__ == "__main__":
    main()
