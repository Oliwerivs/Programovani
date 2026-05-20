/PROG  SVARENI
/ATTR
OWNER		= MNEDITOR;
COMMENT		= "";
PROG_SIZE	= 1205;
CREATE		= DATE 26-02-26  TIME 13:25:28;
MODIFIED	= DATE 26-02-26  TIME 13:25:28;
FILE_NAME	= ;
VERSION		= 0;
LINE_COUNT	= 9;
MEMORY_SIZE	= 1541;
PROTECT		= READ_WRITE;
STORAGE		= SHADOW;
TCD:  STACK_SIZE	= 0,
      TASK_PRIORITY	= 50,
      TIME_SLICE	= 0,
      BUSY_LAMP_OFF	= 0,
      ABORT_REQUEST	= 0,
      PAUSE_REQUEST	= 0;
DEFAULT_GROUP	= 1,*,*,*,*;
CONTROL_CODE	= 00000000 00000000;
LOCAL_REGISTERS	= 0,0,0;
/APPL
  ARC Welding Equipment : 1,*,*,*,*;

MPAS ;
MPAS_NUM_PASSES        : 0;
MPAS_LAST_PASS         : 0;
MPAS_CURRENT_PASS      : 0;
MPAS_STATUS_PASS       : 0;

  AUTOZONE_INTERFERENCE_AVOID;
    AUTOZONE_ENABLED         : FALSE;
    AUTOZONE_SCHEDULE_NUMBER : 1;
/MN
   1:  UFRAME_NUM=0 ;
   2:  UTOOL_NUM=1 ;
   3:   ;
   4:J PR[1:Home] 100% FINE    ;
   5:J P[1] 100% FINE    ;
   6:L P[2] 2000mm/sec FINE    ;
   7:L P[3] 2000mm/sec FINE    ;
   8:J P[4] 100% FINE    ;
   9:J PR[1:Home] 100% FINE    ;
/POS
P[1]{
   GP1:
	UF : 0, UT : 1,		CONFIG : 'N U T, 0, 0, 0',
	X =  1905.819580  mm,	Y =  1001.835083  mm,	Z =   238.304459  mm,
	W =    10.834944 deg,	P =   -59.397449 deg,	R =   -12.536338 deg
};
P[2]{
   GP1:
	UF : 0, UT : 1,		CONFIG : 'N U T, 0, 0, 0',
	X =  2000.389038  mm,	Y =  1001.835266  mm,	Z =   183.704727  mm,
	W =    10.835032 deg,	P =   -59.397694 deg,	R =   -12.536590 deg
};
P[3]{
   GP1:
	UF : 0, UT : 1,		CONFIG : 'N U T, 0, 0, 0',
	X =  2014.347900  mm,	Y =   325.646729  mm,	Z =   207.884857  mm,
	W =    10.835086 deg,	P =   -59.397694 deg,	R =   -12.536640 deg
};
P[4]{
   GP1:
	UF : 0, UT : 1,		CONFIG : 'N U T, 0, 0, 0',
	X =  1898.993896  mm,	Y =   325.646637  mm,	Z =   274.484802  mm,
	W =    10.835040 deg,	P =   -59.397640 deg,	R =   -12.536628 deg
};
/END
