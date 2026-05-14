/PROG  PNP_CYCLE_PACK
/ATTR
OWNER		= MNEDITOR;
COMMENT		= "Na dopravnik";
PROG_SIZE	= 2242;
CREATE		= DATE 25-05-21  TIME 12:36:34;
MODIFIED	= DATE 25-08-29  TIME 11:42:32;
FILE_NAME	= ;
VERSION		= 0;
LINE_COUNT	= 98;
MEMORY_SIZE	= 2794;
PROTECT		= READ_WRITE;
TCD:  STACK_SIZE	= 0,
      TASK_PRIORITY	= 50,
      TIME_SLICE	= 0,
      BUSY_LAMP_OFF	= 0,
      ABORT_REQUEST	= 0,
      PAUSE_REQUEST	= 0;
DEFAULT_GROUP	= 1,*,*,*,*;
CONTROL_CODE	= 00000000 00000000;
/APPL
/APPL
/MN
   1:  LBL[21] ;
   2:  WAIT DI[14:OFF:Odeber]=ON    ;
   3:   ;
   4:  UFRAME_NUM=0 ;
   5:  UTOOL_NUM=1 ;
   6:  PAYLOAD[1] ;
   7:  OVERRIDE=R[5:OVERRIDE] ;
   8:  R[9:Odebrano sacku]=0    ;
   9:   ;
  10:  IF UO[7:OFF:At perch]<>ON,CALL M_RETURN_HOME ;
  11:   ;
  12:  !Loop zakladani ;
  13:  LBL[1:START CYKLU] ;
  14:   ;
  15:  !Zmena UFRAME ;
  16:  UFRAME_NUM=0 ;
  17:   ;
  18:  !Vyhozeni ;
  19:  IF (0<>0) THEN ;
  20:  LBL[2:Vyhozeni] ;
  21:  CALL VYHOZENI    ;
  22:   ;
  23:  R[12:Pocet NOK]=R[12:Pocet NOK]+1    ;
  24:   ;
  25:  ENDIF ;
  26:   ;
  27:  !Nad odebranim ;
  28:  CALL TOOL_OFFSET(0,0,R[2:Z- nad odebranim]) ;
  29:J PR[2:Pick_POS] 100% FINE Tool_Offset,PR[5:Tool Offset]    ;
  30:  DO[12:OFF:NO Pick]=OFF ;
  31:  WAIT GI[2:0:TL.SACKU *0.01]<>0 TIMEOUT,LBL[99] ;
  32:   ;
  33:  !konec cyklu navrat do HP ;
  34:  LBL[22] ;
  35:  IF (DI[14:OFF:Odeber]) THEN ;
  36:  JMP LBL[20] ;
  37:  ELSE ;
  38:  IF (DI[12:OFF:Ukonceni produkce]) THEN ;
  39:  CALL M_RETURN_HOME    ;
  40:  JMP LBL[21] ;
  41:  ENDIF ;
  42:  ENDIF ;
  43:  JMP LBL[22] ;
  44:   ;
  45:  LBL[20] ;
  46:   ;
  47:  WAIT DI[14:OFF:Odeber]=ON    ;
  48:   ;
  49:  IF DI[9:OFF:Sacek_1_OK]=OFF OR DI[10:OFF:Sacek_2_OK]=OFF,JMP LBL[2] ;
  50:   ;
  51:  !Zapnuti vzduchu+odebrani ;
  52:  CALL ZAP_VZDUCH    ;
  53:   ;
  54:  CALL TOOL_OFFSET(0,0,0) ;
  55:L PR[2:Pick_POS] 4000mm/sec FINE Tool_Offset,PR[5:Tool Offset]    ;
  56:   ;
  57:  WAIT    .10(sec) ;
  58:   ;
  59:  F[32:OFF:GRP_P_FULL]=(ON) ;
  60:  F[33:OFF:GRP_L_FULL]=(ON) ;
  61:   ;
  62:  CALL TOOL_OFFSET(0,0,(-20)) ;
  63:L PR[2:Pick_POS] 1000mm/sec CNT100 Tool_Offset,PR[5:Tool Offset]    ;
  64:   ;
  65:  CALL TOOL_OFFSET(0,0,R[2:Z- nad odebranim]) ;
  66:J PR[2:Pick_POS] 100% CNT100 Tool_Offset,PR[5:Tool Offset]    ;
  67:   ;
  68:  IF (R[9:Odebrano sacku]>=GI[1:0:MAX vrstev v krabici]) THEN ;
  69:  R[9:Odebrano sacku]=0    ;
  70:  ENDIF ;
  71:  R[9:Odebrano sacku]=R[9:Odebrano sacku]+1    ;
  72:  !Nad Balicku ;
  73:  //J P[1:nad blicku] 100% CNT100    ;
  74:J P[2] 100% CNT100    ;
  75:  !Vlozit zakladani ;
  76:   ;
  77:  SELECT R[20:Pozadovany_pocet]=1,CALL ODKLADANI_PO_JEDNOM ;
  78:         =3,CALL STOSOVANI_PAS3KS ;
  79:         =5,CALL STOSOVANI_PAS5KS ;
  79:         ELSE,JMP LBL[999];
  80:   ;
  81:  !--------------- ;
  82:   ;
  83:  JMP LBL[1] ;
  84:  !Timeou-Tloustka----------------- ;
  85:  IF (0<>0) THEN ;
  86:  LBL[99] ;
  87:  UALM[1] ;
  88:   ;
  89:  !-------------------------------- ;
  90:  ENDIF ;
  91:  END ;
  92:   ;
  93:  !POZICE NA LUZKEM ODEBRANI ;
  94:   ;
  95:  UFRAME_NUM=0 ;
  96:  UTOOL_NUM=1 ;
  97:L PR[2:Pick_POS] 200mm/sec FINE    ;
  98:  WAIT (OFF)    ;
  98:   ;
  98:  LBL[999];
  98:  UALM[4];
/POS
P[1:"nad blicku"]{
   GP1:
	UF : F, UT : F,		CONFIG : 'N D B, 0, 0, 0',
	X = ********  mm,	Y = ********  mm,	Z = ********  mm,
	W = ******** deg,	P = ******** deg,	R = ******** deg
};
P[2]{
   GP1:
	UF : F, UT : F,		CONFIG : 'N D B, 0, 0, 0',
	X = ********  mm,	Y = ********  mm,	Z = ********  mm,
	W = ******** deg,	P = ******** deg,	R = ******** deg
};
/END
