#!/usr/bin/python
#-*- coding: utf-8 -*-




#hello and welcome



import ply.yacc as yacc
from ply.lex import LexToken
import pygame
import simplejson #save/restore


class Token(LexToken):
	def __init__(self, type, value, line):
		self.type = type
		self.value = value
		self.line = line


def yield_code(code):
	for line in code:
		for i, item in enumerate(line):
			if item[1] <> None: 
				yield Token(item[1], item[0], i)
		yield Token("newline", "banana", i)
	yield None




def parse_code(code):
	print "code:",code
	code_yielder = yield_code(code)
	print parser.parse(tokenfunc=code_yielder.next,lexer=3)





def p_expression_plus(p):
	'expression : expression plus term'
	p[0] = p[1] + p[3]

def p_expression_minus(p):
	'expression : expression minus term'
	p[0] = p[1] - p[3]

def p_expression_term(p):
	'expression : term'
	p[0] = p[1]

def p_term_times(p):
	'term : term times factor'
	p[0] = p[1] * p[3]

def p_term_div(p):
	'term : term divide factor'
	p[0] = p[1] / p[3]

def p_term_factor(p):
	'term : factor'
	p[0] = p[1]

def p_factor_num(p):
	'factor : number'
	p[0] = p[1]

def p_factor_expr(p):
	'factor : left_parenthesis expression right_parenthesis'
	p[0] = p[2]

def p_error(p):
	print "Syntax error in input!"

def p_statement(p):
	"""statement    : kind_declaration
			| thing_declaration
			| expression
			| statement newlines statement"""
	p[0] = p[1]

def p_newline_eater(p):
	"""newlines     : newline newline
			| newline"""

class KindDeclaration:
	pass

class ThingDeclaration:
	pass

def p_kind_declaration(p):
	'kind_declaration : something_new is_a_kind_of kind'
	p[0] = KindDeclaration()
	p[0].parent = p[3]
	p[0].child = p[1]

def p_thing_declaration(p):
	'thing_declaration : something_new is kind'
	p[0] = ThingDeclaration()
	p[0].kind = p[3]
	p[0].name = p[1]

def p_array_declaration(p):
	'array_declaration      : something_new is_an_array
				| something_new is_an_array of kind'


def p_integer_declaration(p):
	'integer_declaration	: something_new is_an_integer
				| something_new is_an_integer in_range number-number
				| something_new is_an_integer between number and number'


def p_open_file_statement(p):
	'open_file_statement	: open path_to_file
				| open path_to_file as file_handle'


class BananaTable():
	pass

class BananaTableColumn():
	pass

def p_table_column(p):
	'table_column: name - type'
	p[0] = BananaTableColumn()
	p[0].name = p[1]
	p[0].type = p[3]

def p_table_column2(p):
	'table_column2: name ( type )'
	p[0] = BananaTableColumn()
	p[0].name = p[1]
	p[0].type = p[3]

def p_table_name(p):
	'table_name	: table of something_new'
	p[0] = p[3]

def p_table_columns(p):
	'table_columns  : table_columns table_column
			|table_columns table_column2
			|table_column 
			|table_column2'

def p_table_heading(p):
	'table_heading	: table_columns'
	p[0] = BananaTable()
	p[0].name = p[3]


def p_table_declaration(p):
	'table_declaration	: table_heading newline table_data'
	p[0] = BananaTable()
	p[0].name = p[3]



tokens = ['newline', 'something_new', 'is', 'kind', 'is_a_kind_of']



class BananaArray():
	def __init__(self):
		self.array = []


#program interpreter environment
environment = {
	"rules":
	{	
		"program begins": [],
		"program ends": []
	}
	"variables":
	{
		"banana color" : "yellow"
	}
}



def interpret(ast):
	for x in ast:
		if type(x) is ThingDeclaration:
			if x.kind == "array"


#the static part of the menu, more stuff gets added by parsing the program
#it goes hardcoded -> dictionary -> menu
hardcoded = [[a,a] for a in ["is a kind of","is"]]
hardcoded +=[["a", "particle"],["an","particle"],["thing","kind"]]


hardcoded += [["when", "when"]]+ [[i,"rule"] for i,j in environment["rules"].items()]

somethings = [['+', 'plus'],['-','minus'],['*','times'],['/','divide'],['(','left_parenthesis'],['(','right_parenthesis']]
hardcoded +=  [[i[0],i[0]] for i in somethings]
tokens +=  [i[1] for i in somethings]
tokens += ['number']
print tokens

print "dict is", hardcoded
dictionary = hardcoded[:]



patterns={
"kind declaration": ["something new", "is a kind of", "kind"],
"object declaration": ["something new", "is", "particle", "kind"],
#"rule": ["when", "rule", 
}





parser = yacc.yacc()





def parse():
	parse_code(code)





#	for line in code:
#		if matches(line, patterns["kind declaration"]):
#			dictionary.append([line[0][0], "kind"])
#		if matches(line, patterns["object declaration"]):
#			dictionary.append([line[0][0], line[3][0]])



def update_dictionary():
	global dictionary
	dictionary = hardcoded[:]
	parse()

	print "dictionary is ", dictionary

def update_menu():
	global menu
#	make a list of all dictionary words beginning with the edited word
	menu = [i for i in dictionary if get_text() in i[0]]
	print "todays menu:", menu




def update_menu_sel():
	global menu_sel
	menu_sel = -1
	counter = 0
	for i in menu:
		if i[0] == get_text():
			menu_sel = counter
		counter += 1 

def menu_choice():
	set_meaning(menu[menu_sel][1])
	set_text(menu[menu_sel][0])

def change_the_past():
	for (i,j) in dictionary:
		
		pass



def confirm_choice():
	global menu_sel
	if menu_sel <> -1:
		menu_choice()
		menu_sel = -1
	else:
		set_meaning("something new")
	change_the_past()



def initiate_new_word():
	menu_sel = 0


def create_cell(y,x):
	while wordy >= len(code):
		code.append([])
	while wordx >= len(code[y]):
		code[y].insert([])


def set_meaning(x):
	global code
	create_cell(wordy, wordx)
	code[wordy][wordx][1] = x
	print "meaning set to", x


def set_text(w):
	global code
	create_cell(wordy, wordx)
	code[wordy][wordx][0] = w


def get_text():
	if (wordy < len(code)) and wordx < len(code[wordy]):
		return code[wordy][wordx][0]
	else
		return ""




def get_line_len(y):
	if len(code) > y:
		return len(code[y])
	else:
		return 0



#moving about


def snap_to_line():
	#if number_of_letters_on_line(wordy) < number_of_letters_on_previous_line...
	global wordx, cursorx
	#if wordx > len(code[wordy])
	#wordx = min(get_line_len(wordy), wordx)
	cursorx=wordx=0

def moveup():
	global wordy
	if wordy <> 0:
		wordy-=1
	snap_to_line()

def movedown():
	global wordy, code, wordx
	wordy+=1
	if wordy >= len(code):
		code.append([])
	#k
	snap_to_line()


def moveright():
	global cursorx
	if cursorx < len(code[wordy][wordx][0]):
		print "cursorx += 1"
		cursorx += 1
	else:
		wordright()
def wordright():
	global wordx, code, cursorx
#	print "wordright"
	wordx += 1
	cursorx = 0
	stretch_line()

def moveleft():
	global cursorx
	if cursorx > 0:
		cursorx -= 1
	else:	
		wordleft()

def wordleft():
	global wordx, cursorx
	if wordx > 0:
		wordx -= 1
		cursorx = len(code[wordy][wordx][0])














#drawing

def getletters():
	letters = 0
	for i in range(0, wordx):
		letters += len(code[wordy][i][0])+1
	return letters




def draw():
	screen_surface.fill((0,0,0))
	lines_for_each_line = 3
#text
	y = 0
	wy = 0
	for l in code:
		x = left_margin
		wx = 0
		for wx,w in enumerate(l):
			
			#draw a debug rectangle around the word
			pygame.draw.rect(screen_surface, (0,0,200), (x,y,len(w[0])*fontw, fonth), 2)

			#draw word text
			if w[0] == "":
				to_blit_get_width = 0
			else:
				if (wx == wordx) and (wy == wordy):
					color = (255,255,255)
				else:
					color = (122,255,122)
				to_blit=font.render(w[0],True,color)
				screen_surface.blit(to_blit,(x, y))
				to_blit_get_width = to_blit.get_width()

			#draw meaning under it
			to_blit=font.render(w[1],True,(0,0,200))
			screen_surface.blit(to_blit,(x, y+fonth))
		
			x = x + to_blit_get_width + fontw
		y += fonth*lines_for_each_line
		wy += 1

#cursor
	letters = getletters() + cursorx
	#print "cursorx is ",cursorx,", drawing cursor at ",letters," letters"	
	startpos = (left_margin+(letters*fontw), wordy*lines_for_each_line*fonth)
	endpos   = (left_margin+(letters*fontw), (wordy*lines_for_each_line+1)*fonth)
	pygame.draw.aaline(screen_surface, (200, 200, 0), startpos, endpos,3)

#menu
	letters = getletters()
	#wordy * fonth is the y position of the current word
	counter = 0
	for i in menu:
		if counter == menu_sel:
			color = (255,0,0)
		else:
			color = (200,0,0)
		to_blit=font.render(i[0],True,color)
		y = (wordy*lines_for_each_line+counter+1) * fonth
		x = left_margin + letters * fontw
		screen_surface.blit(to_blit,(x, y))
		counter += 1





	pygame.display.update()








#key input


def control(event):
	global menu_sel,cursorx,code, wordx,wordy


	# up & down
	if event.key == pygame.K_DOWN:
		movedown()
	elif event.key == pygame.K_UP:
		moveup()

	# pg up & down
	elif event.key == pygame.K_PAGEDOWN:
		menu_sel +=1
	elif event.key == pygame.K_PAGEUP:
		menu_sel -=1

	# left & right
	elif event.key == pygame.K_LEFT:
		moveleft()
	elif event.key == pygame.K_RIGHT:
		moveright()




	elif event.key == pygame.K_HOME:
		cursorx = 0
		wordx = 0
	elif event.key == pygame.K_END:
		wordx = -1+len(code[wordy])
		cursorx = len(get_text())



	elif event.key == pygame.K_F8:
	        del code[wordy]



	elif event.scancode == 151 or event.key == pygame.K_F12:
	        #exit
#		save()
		bye()
	elif event.key == pygame.K_F10:
 		bye()

#	print "scancode ", event.scancode
	
	elif event.unicode == ' ':
		confirm_choice()
		wordright()

	elif event.key == pygame.K_RETURN:
		if pygame.key.get_mods() & pygame.KMOD_RCTRL:
			parse()
		else:
			confirm_choice()
			wordy+=1
			wordx=0
			cursorx=0
			code.insert(wordy, [])
			snap_to_line()
			stretch_line()

	else: return False		

	update_menu()
	return True


def edit(event):
	global cursorx
	if event.key==pygame.K_BACKSPACE:
		print "backspace"
		if cursorx > 0:
			if cursorx <= len(get_text()):
				newtext = get_text()[0:cursorx-1]+get_text()[cursorx:]
				#print get_text(), "->", newtext
				set_text(newtext)
				cursorx -=1
		else:
			if wordx > 0:
				#print ">0"
				#print code[wordy][wordx-1]
				if code[wordy][wordx][0]=="":
					#print "del"
					del code[wordy][wordx]
					moveleft()
			else:
				if wordy > 0:
					if code[wordy-1][len(code[wordy-1]-1)]:

	elif event.key==pygame.K_DELETE:
		if cursorx >= 0 and cursorx < len(get_text()):
			set_text(get_text()[0:cursorx]+get_text()[cursorx+1:])
	elif event.unicode:
		set_text(get_text()[0:cursorx]+event.unicode+get_text()[cursorx:])
		cursorx +=1
	else:
		return

	update_dictionary()
	update_menu()
	update_menu_sel()



def mouse_me_baby(event):
	global menu_sel
	print event
	if event.button == 4: #up
		menu_sel -= 1
	if event.button == 5: #down
		menu_sel += 1





def process_event(event):
	if event.type == pygame.QUIT:
		bye()
	if event.type == pygame.KEYDOWN:
		control(event) or edit(event)
	if event.type == pygame.MOUSEBUTTONDOWN:
		mouse_me_baby(event)








#margin between displayed text and left edge of the window
left_margin = 10
screen_height = 480







def init_window():
	pygame.init()
	pygame.display.set_caption("secret-banana")
	#sdl, which pygame is based on, has its own keyboard delay and repeat rate
	pygame.key.set_repeat(300,30)
	#this creates a window
	return pygame.display.set_mode((640,screen_height))

screen_surface = init_window()





def init_font():
	#the final version is planned to use comic sans ✈
	font = pygame.font.SysFont('monospace', 16)
	f= font.render(" ",False,(0,0,0)).get_rect()
	fonth = f.height
	fontw = f.width
	return font, fontw, fonth

(font, fontw, fonth) = init_font()








try:
	code = simplejson.loads(open("code.json", "r").read())
except:
	code = [[[3,"number"],["+", "plus"],[3, "number"]]]




#cursor position in the current word
cursorx = 0
#the current word on line
wordx = 0
#line
wordy = 0





#the red menu
menu = []
#selected item. -1 for none
menu_sel = 0





def loop():
	process_event(pygame.event.wait())
	draw()








update_menu()






pygame.time.set_timer(pygame.USEREVENT, 40)#SIGINT timer





def bye():
	open("code.json", "w").write(simplejson.dumps(code))
	exit()





while 1:
	try:
		loop()
	except KeyboardInterrupt() as e:
		pygame.display.iconify()
		raise e
	except Exception() as e:
		pass













"""
#todo:
if key.unicode == '\':
	cursor left
	add newline
	cursor up

"""			