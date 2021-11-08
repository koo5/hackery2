"use strict"

const fs = require('fs')
var parse = require('dotparser');
var ast = parse(fs.readFileSync('test.gv', 'utf8'));
console.log(ast);
let g = ast[0].children
let nodepairs = {};
g.forEach((stmt) =>
{
	let el = stmt.edge_list;
	//console.log(el)
	if (el)
	{
		//console.log(el)
		let node0;
		el.forEach(e =>
		{
			if (node0 !== undefined)
			{
				let pair = JSON.stringify({'src': node0, 'tgt': e});
				//console.log(pair)
				if (nodepairs.hasOwnProperty(pair))
					console.log(pair);
				nodepairs[pair] = true;
			}
			node0 = e;
		})
	}
});
