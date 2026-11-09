/PROG  T_OFFSET	  Macro
/ATTR
OWNER		= MNEDITOR;
COMMENT		= "Tool Offset";
PROG_SIZE	= 176;
CREATE		= DATE 26-09-04  TIME 10:21:02;
MODIFIED	= DATE 26-09-04  TIME 10:21:18;
FILE_NAME	= ;
VERSION		= 0;
LINE_COUNT	= 0;
MEMORY_SIZE	= 420;
PROTECT		= READ_WRITE;
TCD:  STACK_SIZE	= 0,
      TASK_PRIORITY	= 50,
      TIME_SLICE	= 0,
      BUSY_LAMP_OFF	= 0,
      ABORT_REQUEST	= 0,
      PAUSE_REQUEST	= 0;
DEFAULT_GROUP	= 1,*,*,*,*;
CONTROL_CODE	= 00000000 00000000;
LOCAL_REGISTERS	= 0,1,0;
/APPL
  ARC Welding Equipment : 1,*,*,*,*;
/MN
1:  !Tool Offset macro;
2:  !This macro is used to set the tool offset for the laser head;
3:  PR[11:Tool Offset]=PR[11:Tool Offset]-PR[11:Tool Offset] ;
4:  PR[11,1:Tool Offset]=AR[1];
5:  PR[11,2:Tool Offset]=AR[2];;
6:  PR[11,3:Tool Offset]=AR[3];;
/POS
/END
