--ok, anything that isnt clear? not really. If a problem comes up we'll just go to #haskell, or, as i call it, hashkell:)
--so it works now? we just need to add more Instr's? well i dunno if we wanna add an...what is it even... for every instructi
--on, or --Oooh, we need the flags; they are set based off of the prev. instruction's result; if we 'cmp' 2 numbers
-- and they're not equal, we set the NE flag. did you say the VM should be realistic as in registerless? could the flags be 
--just more memory locations? sure -- lets do the naming somehow -- MemLoc....mmm... maybe we could make a malloc function, only 
--problem is, since haskell functions can't have side-effects, that'd be really hard. nothing hard about it #maybe it's doable:)
import Data.List
import Data.Char
import Data.Int
import Debug.Hood.Observe
import Safe
import Data.Bits --? --what? when? how? shift left/right; >> and << don't mean what they do in other langs--ahh

--We'll worry about modules when it's done
--data InstrDetails  = InstrDetails {instrName :: String, opcode :: Int} --That should be sufficient

rACC = 0--well, this could work...  What other registers besides ACC and a general purpose one will we need?dunno, your expertise:)
rGPA = 1 -- General purpose register 'a'
rGPB = 2 -- take a fuckin guess
rGPC = 3 -- original
rSPR = 4 -- stack pointer
rFNE = 5 --6why not just fNE? because reasons
rFEQ = 6
rFLT = 7
rFGT = 8
rFCK = 9--i lol'd --9/10 would lol again
rRES = 10 --result of last operation; this means rFCK is deprecated, althought someone has yet to submit a patch--
--an error register will prolly still be useful, even with ints.anyway..
--I came up with a way to set your own flags:
--the `tog' instruction: it toggles a global boolean; starts out false
--i was thinking about a register for error messages yesterday when we were having trouble with debugging, 
--but then the memory is just ints
--any others you can think of?rFCK, but i cant figure out a good use
--maybe rFCK is set when you divide by zero
--all the flags are 2 letters and the flag regnames start with f

showRegs regs =
	"ACC: " ++ show (regs !! rACC)

type MemLoc        = Int
data Literal       = IntLit Int | CharLit Char | StrLit String deriving (Eq, Show)
		--back in a bit k
data Operand       = Loc MemLoc | Lit Literal deriving (Eq, Show)-- An operand (or argument) of an assembly instruction 
type Opcode        = Int
--do we just define all the instructions here ? that seems a bit weird though...
--it would be a standard way for a higher level interpreter --why not
 --why not define them all here? thats what i just said --i'm agreeing with you--ah..well it would look like this..
type Op            = Operand  --what are you doing in mc?extracting some something for the forms thing --i'm more noob than you; i can't use mcedit.yea thats a whole new nooblevel
--that was probably the weirdest thing that happened today--im so sleepy man--
--soon i'm gonna go to best buy and gaze longingly at the awesome expensive mechanical keyboards--they have mechanical keyboards at bestbuy?
--they do here
--they have one that's out in the open that you can clack on
--and another more clacky brand thats not out, but you can press the arrow keys through the box--haha ok. im off. have fun okay bye

data InstrType     = Nop | Add Op Op | Min Op Op | Cal | Psh Op | Sub String | End | Mul Op Op | Shl Op Op | Shr Op Op | Cmp Op Op | Tog | deriving (Eq, Show)
--sub "name" ?well a string then i suppose
--mov dest, src
--data RegisterDef   = Register {name :: String, value :: [Int], id} --TODO?
type RegisterType  = Int -- wont memory be all of one type anyway? -- RegisterType; don't change
type Registers     = [RegisterType] -- Register contents
data VmType        = Vm {instrPointer :: Int, regs :: Registers} deriving (Show, Eq) -- Virtual machine instance description

someMem = replicate 1001 0
newVm = Vm 0 someMem

evalAsm   :: String -> VmType -> VmType

evalAsm asmText vm = let
	--since when is asm a keyword in haskell?:D
	lns = lines asmText -- Tharnk you haskell stdlib --this is nice. --that was stupid--what happened?--i spaced out for a bit
	--instrs = map (observe "parse"  parseStrToInstruction) lns
	in
		evalAsmLines lns vm

evalAsmLines lns vm =
	let
		instrs = map parseStrToInstruction lns
	in
		evalInstructions instrs vm

evalInstructions :: [InstrType] -> VmType -> VmType

evalInstructions [] vm = vm

evalInstructions instrs vm =
	let ip = instrPointer vm in
		if length instrs > ip then
			evalInstructions instrs $ runBinary (instrs !! ip) vm
		else
			vm

updated list pos val =
	take pos list ++ [val] ++ drop (pos + 1) list

---test0 (Instr a b c) z = print a

test1 =
	let test = Vm 0 [3,4,5] in
		print test


locval (Loc ( val)) = val

intval :: Operand -> Int
intval (Lit (IntLit val)) = val

--intlit :: Int -> Lit
--intLit i = Lit $ IntLit i

subs = []

findSub name instrs =
	elemIndex (Sub name) instrs

regFromInt :: Int -> RegisterType

regFromInt x = x

{-
'System call' numbers:
1: Prints top of stack
2: Reads in a line, and places into GPA
3: Reads in a single char, and places into GPA
4: Opens a file: Top of stack is popped 2 times; 1st being the filename, 2nd being the mode (r, w, a)
5: Exit, top of stack is the exit code
-}

runBinary :: InstrType -> VmType -> VmType
--What are you committing to? a repo..
runBinary i (Vm ip regs) = let
		next = ip + 1 
	in case i of
		Nop     -> Vm (ip + 1) regs
		Add a b -> Vm (ip + 1) (updated regs rACC (regFromInt ((intval a)+(intval b))))
		Min a b -> Vm (ip + 1) (updated regs rACC (regFromInt ((intval a)-(intval b))))
		Cal     -> Vm next (updated regs 666 666) --srsly do we have to call
		--functions by some obscure number when it can be a nice string and even
		--have separate system and user functions? what is this, 1920's?
		--it's how x86 asm is...and?   
		Psh x   -> Vm next (updated regs 667 666)
		Sub _   -> Vm next regs
		End     -> Vm next regs
		Shr a b -> Vm next (updated regs rACC (regFromInt ((intval a)`shiftR`(intval b))))
		Shl a b -> Vm next (updated regs rACC (regFromInt ((intval a)`shiftL`(intval b)))) --those should work...--try it out...
		Cmp a b -> Vm next (updated flags r --maybe call a function that returns a list of flags?
		--personally id just be lazy and use the main mem. rCMP or something
		--Things can set multiple flags you know: cmp 5, 4 makes the LT and NE flags 'true'--so? use multiple flags.
		--multiple flag registers? 'cause that's not a bad idea.orly?rly.kay
--Could you tell me some of mcedits shortcuts?
--look down
--i don't know why i'm surprised that didnt work...--what didint work? pressing 1 for help f1 ooooooooooooooooohhhhhh
-- Min Op Op | Cal | Psh Op | Sub String | End deriving (Eq, Show)

parseStrToInstruction :: String -> InstrType

parseStrToInstruction s = do
	let x = words s
	    i = observe "i" (x !! 0)
	    o1str = x !! 1
	    o2str = x !! 2
	    o1 = readNote (show x) o1str :: Int
	    o2 = readNote (show x) o2str :: Int
	     in
	     	
		case i of
			"" -> Nop
			"---" -> Nop
			"nop" -> Nop
			"add" -> Add (Lit(IntLit o1)) (Lit(IntLit o2))
			"min" -> Min (Lit(IntLit o1)) (Lit(IntLit o2))

			"psh" -> Psh (Lit(StrLit o1str))
			"cal" -> Cal
			--we need to make a stack...--cal <thing> : executes a 'system call'
			"sub" -> Sub o1str
			"end" -> End
	--i = x
	--y = x !! 0:x !! 1:x !! 2 --without a simple slicing notation, this is the best i got. 3.
	--z = Instr y !! 0 y !! 1 y !! 2


--testParse =
--	parseStrToInstruction "add 3 3" == Add Lit

--readAndExecuteOperationFromStr :: String -> VmType -> VmType

--readAndExectueOperationFromStr str vm = do
--	runBinary parseStrToInstruction vm

--test2 = do
--	print testParse
--	let myRegisters = [0]
--	    vm          = Vm 0 myRegisters in do --Should work...
	    --print evalAsm "add x y" vm -- for later
	    --print $ runBinary Instr 0 00 0 vm --Right? will see.
  --          print $ runBinary (Instr 0 (Loc 0) (Lit (IntLit 0))) vm
--	    let vm2 = runBinary (Instr 1 (Lit (IntLit 6)) (Lit (IntLit 3)) ) vm in
--	            print $ runBinary (Instr 1 (Lit (IntLit 6)) (Lit (IntLit 3)) ) vm2 --add 6 and 3 and put to ACC(0)
 


--The archaic way
test4 = 
	evalAsmLines ["add 3 5",
	"sub \"mysub\"",
	"psh \"Hey\"",
	"cal \"print\"",
	"end",
	"--- jmp \"mylabel\""] newVm
--shoulnt the \'s be at the end of lines?
--There. crude.



main = do
	--print $ (read "34" :: Int)
	let vm = test4
	print vm
	print $ showRegs $ regs vm


oo = runO main




