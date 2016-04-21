BEGIN TRANSACTION;
CREATE TABLE `TheoryIndex` (
	`ID`		INTEGER NOT NULL UNIQUE,
	`PTO`		INTEGER NOT NULL,
	`FNS`		TEXT 	NOT NULL,
	`DAMP`		INTEGER NOT NULL,
	`IC`		INTEGER NOT NULL,
	`ModEv`		TEXT 	NOT NULL,
	`XIR`		REAL 	NOT NULL,
	`XIF`		REAL 	NOT NULL,
	`NfFF`		INTEGER NOT NULL,
	`MaxNfAs`	INTEGER NOT NULL,
	`MaxNfPdf`	INTEGER NOT NULL,
	`Q0`		REAL 	NOT NULL,
	`alphas`	REAL 	NOT NULL,
	`Qref`		REAL 	NOT NULL,
	`QED`		INTEGER NOT NULL,
	`alphaqed`	REAL 	NOT NULL,
	`Qedref`	REAL 	NOT NULL,
	`SxRes`		INTEGER NOT NULL,
	`SxOrd`		TEXT 	NOT NULL,
	`HQ`		TEXT 	NOT NULL,
	`mc`		REAL 	NOT NULL,
	`Qmc`		REAL 	NOT NULL,
	`kcThr`		REAL 	NOT NULL,
	`mb`		REAL 	NOT NULL,
	`Qmb`		REAL 	NOT NULL,
	`kbThr`		REAL 	NOT NULL,
	`mt`		REAL 	NOT NULL,
	`Qmt`		REAL 	NOT NULL,
	`ktThr`		REAL 	NOT NULL,
	`CKM`		TEXT 	NOT NULL,
	`MZ`		REAL 	NOT NULL,
	`MW`		REAL 	NOT NULL,
	`GF`		REAL 	NOT NULL,
	`SIN2TW`	REAL 	NOT NULL,
	`TMC`		INTEGER NOT NULL,
	`MP`		REAL 	NOT NULL,
	`Comments`	TEXT,
	/* Primary Key */
	PRIMARY KEY(ID),
	/* Checks */
	CHECK(PTO IN ( 0 , 1 , 2 )),
	CHECK(FNS IN ( 'FFNS' , 'ZM-VFNS' , 'FONLL-A' , 'FONLL-B' , 'FONLL-C' )),
	CHECK(DAMP IN ( 0 , 1 )),
	CHECK(IC IN ( 0 , 1 )),
	CHECK(ModEv IN ( 'EXA' , 'EXP' , 'TRN' )),
	CHECK(XIR > 0),
	CHECK(XIF > 0),
	CHECK(NfFF IN ( 3 , 4 , 5 , 6 )),
	CHECK(MaxNfAs IN ( 3 , 4 , 5 , 6 )),
	CHECK(MaxNfPdf IN ( 3 , 4 , 5 , 6 )),
	CHECK(Q0 > 0),
	CHECK(alphas > 0 AND alphas < 1),
	CHECK(Qref > 0),
	CHECK(QED IN ( 0 , 1 )),
	CHECK(alphaqed > 0 AND alphaqed < 1),
	CHECK(Qedref > 0),
	CHECK(SxRes IN ( 0 , 1 )),
	CHECK(SxOrd IN ( 'LL' , 'NLL' , 'NNLL' )),
	CHECK(HQ IN ( 'POLE' , 'MSBAR' )),
	CHECK(mc > 0),
	CHECK(Qmc >= 0),
	CHECK(kcThr >= 0),
	CHECK(mb > 0),
	CHECK(Qmb >= 0),
	CHECK(kbThr >= 0),
	CHECK(mt > 0),
	CHECK(Qmt >= 0),
	CHECK(ktThr >= 0),
	CHECK(MZ > 0),
	CHECK(MW > 0),
	CHECK(GF > 0),
	CHECK(SIN2TW > 0 AND SIN2TW < 1),
	CHECK(TMC IN ( 0 , 1 )),
	CHECK(MP > 0)
);
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (1,0,'ZM-VFNS',0,0,'TRN',1.0,1.0,5,5,5,1.0,0.118,91.2,0,0.007496252,1.777,0,'LL','POLE',1.275,1.275,1.0,4.18,4.18,1.0,173.07,173.07,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'3.0 LO benchmark');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (2,1,'FONLL-B',1,0,'TRN',1.0,1.0,5,5,5,1.0,0.118,91.2,0,0.007496252,1.777,0,'LL','POLE',1.275,1.275,1.0,4.18,4.18,1.0,173.07,173.07,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'3.0 NLO benchmark');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (3,2,'FONLL-C',1,0,'TRN',1.0,1.0,5,5,5,1.0,0.118,91.2,0,0.007496252,1.777,0,'LL','POLE',1.275,1.275,1.0,4.18,4.18,1.0,173.07,173.07,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'3.0 NNLO benchmark');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (4,1,'FONLL-B',1,0,'TRN',1.0,1.0,5,5,5,1.3,0.118,91.2,0,0.007496252,1.777,0,'LL','POLE',1.275,1.275,1.0,4.18,4.18,1.0,173.07,173.07,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'3.0 NLO - Q0=1.3 For IC Test');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (5,2,'FONLL-C',1,0,'TRN',1.0,1.0,5,5,5,1.3,0.118,91.2,0,0.007496252,1.777,0,'LL','POLE',1.275,1.275,1.0,4.18,4.18,1.0,173.07,173.07,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'3.0 NNLO - Q0=1.3 For IC Test');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (6,1,'FONLL-B',1,0,'TRN',1.0,1.0,5,5,5,1.0,0.118,91.2,0,0.007496252,1.777,0,'LL','MSBAR',0.986,3.0,1.0,4.18,4.18,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'3.0 NLO - HXSWG MSBar Masses');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (7,2,'FONLL-C',1,0,'TRN',1.0,1.0,5,5,5,1.0,0.118,91.2,0,0.007496252,1.777,0,'LL','MSBAR',0.986,3.0,1.0,4.18,4.18,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'3.0 NNLO - HXSWG MSBar Masses');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (8,1,'FONLL-B',1,0,'TRN',1.0,1.0,5,5,5,1.0,0.1165,91.2,0,0.007496252,1.777,0,'LL','MSBAR',0.986,3.0,1.0,4.18,4.18,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'3.0 NLO MSBAR (-1sig alpha_S)');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (9,2,'FONLL-C',1,0,'TRN',1.0,1.0,5,5,5,1.0,0.1165,91.2,0,0.007496252,1.777,0,'LL','MSBAR',0.986,3.0,1.0,4.18,4.18,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'3.0 NNLO MSBAR (-1sig alpha_S)');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (10,1,'FONLL-B',1,0,'TRN',1.0,1.0,5,5,5,1.0,0.1195,91.2,0,0.007496252,1.777,0,'LL','MSBAR',0.986,3.0,1.0,4.18,4.18,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'3.0 NLO MSBAR (+1sig alpha_S)');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (11,2,'FONLL-C',1,0,'TRN',1.0,1.0,5,5,5,1.0,0.1195,91.2,0,0.007496252,1.777,0,'LL','MSBAR',0.986,3.0,1.0,4.18,4.18,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'3.0 NNLO MSBAR (+1sig alpha_S)');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (12,1,'FONLL-B',1,0,'TRN',1.0,1.0,5,5,5,1.0,0.118,91.2,0,0.007496252,1.777,0,'LL','MSBAR',0.934,3.0,1.0,4.18,4.18,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'3.0 NLO MSBAR (-2sig mb)');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (13,2,'FONLL-C',1,0,'TRN',1.0,1.0,5,5,5,1.0,0.118,91.2,0,0.007496252,1.777,0,'LL','MSBAR',0.934,3.0,1.0,4.18,4.18,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'3.0 NNLO MSBAR (-2sig mb)');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (14,1,'FONLL-B',1,0,'TRN',1.0,1.0,5,5,5,1.0,0.118,91.2,0,0.007496252,1.777,0,'LL','MSBAR',1.038,3.0,1.0,4.18,4.18,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'3.0 NLO MSBAR (+2sig mb)');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (15,2,'FONLL-C',1,0,'TRN',1.0,1.0,5,5,5,1.0,0.118,91.2,0,0.007496252,1.777,0,'LL','MSBAR',1.038,3.0,1.0,4.18,4.18,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'3.0 NNLO MSBAR (+2sig mb)');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (16,1,'FONLL-B',1,0,'TRN',1.0,1.0,5,5,5,1.0,0.118,91.2,0,0.007496252,1.777,0,'LL','MSBAR',0.986,3.0,1.0,4.12,4.12,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'3.0 NLO MSBAR (-2sig mc)');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (17,2,'FONLL-C',1,0,'TRN',1.0,1.0,5,5,5,1.0,0.118,91.2,0,0.007496252,1.777,0,'LL','MSBAR',0.986,3.0,1.0,4.12,4.12,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'3.0 NNLO MSBAR (-2sig mc)');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (18,1,'FONLL-B',1,0,'TRN',1.0,1.0,5,5,5,1.0,0.118,91.2,0,0.007496252,1.777,0,'LL','MSBAR',0.986,3.0,1.0,4.24,4.24,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'3.0 NLO MSBAR (+2sig mc)');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (19,2,'FONLL-C',1,0,'TRN',1.0,1.0,5,5,5,1.0,0.118,91.2,0,0.007496252,1.777,0,'LL','MSBAR',0.986,3.0,1.0,4.24,4.24,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'3.0 NNLO MSBAR (+2sig mc)');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (20,1,'FONLL-B',1,0,'TRN',1.0,1.0,5,5,5,1.0,0.118,91.2,0,0.007496252,1.777,0,'LL','MSBAR',1.275,1.275,1.0,4.18,4.18,1.0,173.07,173.07,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'3.0 NLO - MSBar masses with Pole values');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (21,2,'FONLL-C',1,0,'TRN',1.0,1.0,5,5,5,1.0,0.118,91.2,0,0.007496252,1.777,0,'LL','MSBAR',1.275,1.275,1.0,4.18,4.18,1.0,173.07,173.07,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'3.0 NNLO - MSBar masses with Pole values');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (22,0,'ZM-VFNS',0,0,'EXA',1.0,1.0,5,5,5,1.275,0.118,91.2,0,0.007496252,1.777,0,'LL','POLE',1.275,1.275,1.0,4.18,4.18,1.0,173.07,173.07,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'LO baseline for small-x res');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (23,0,'ZM-VFNS',0,0,'EXA',1.0,1.0,5,5,5,1.275,0.118,91.2,0,0.007496252,1.777,1,'LL','POLE',1.275,1.275,1.0,4.18,4.18,1.0,173.07,173.07,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'LO+LL for small-x res');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (24,1,'FONLL-B',1,0,'EXA',1.0,1.0,5,5,5,1.275,0.118,91.2,0,0.007496252,1.777,0,'LL','POLE',1.275,1.275,1.0,4.18,4.18,1.0,173.07,173.07,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'NLO baseline for small-x res');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (25,1,'FONLL-B',1,0,'EXA',1.0,1.0,5,5,5,1.275,0.118,91.2,0,0.007496252,1.777,1,'NLL','POLE',1.275,1.275,1.0,4.18,4.18,1.0,173.07,173.07,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'NLO+NLL for small-x res');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (26,1,'FONLL-B',1,0,'EXA',1.0,1.0,5,5,5,1.6,0.118,91.2,0,0.007496252,1.777,0,'LL','POLE',1.6,1.6,1.0,4.18,4.18,1.0,173.07,173.07,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'NLO baseline for small-x, mc=1.6');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (27,1,'FONLL-B',1,0,'EXA',1.0,1.0,5,5,5,1.414,0.118,91.2,0,0.007496252,1.777,1,'NLL','POLE',1.414,1.414,1.0,4.18,4.18,1.0,173.07,173.07,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'NLO+NLL for small-x, mc=1.414');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (28,1,'FONLL-B',1,0,'TRN',1.0,1.0,5,5,5,1.6,0.118,91.2,0,0.007496252,1.777,1,'NLL','POLE',1.6,1.6,1.0,4.18,4.18,1.0,173.07,173.07,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'NLO+NLL for small-x, mc = 1.6');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (29,1,'FONLL-B',1,0,'EXA',1.0,1.0,5,5,5,1.6,0.118,91.2,0,0.007496252,1.777,1,'NLL','POLE',1.6,1.6,1.0,4.18,4.18,1.0,173.07,173.07,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'NLO+NLL for small-x, mc = 1.6');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (30,1,'FONLL-B',1,0,'EXA',1.0,1.0,5,5,5,1.0,0.118,91.2,0,0.007496252,1.777,0,'LL','POLE',1.6,1.6,1.0,4.18,4.18,1.0,173.07,173.07,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'NLO baseline for small-x, Q0=1, mc = 1.6');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (31,1,'FONLL-B',1,0,'EXA',1.0,1.0,5,5,5,1.43,0.118,91.2,0,0.007496252,1.777,0,'LL','POLE',1.43,1.43,1.0,4.18,4.18,1.0,173.07,173.07,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'NLO+NLL for small-x, Q0=mc=1.43');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (32,1,'FONLL-B',1,1,'TRN',1.0,1.0,5,5,5,1.5,0.118,91.2,0,0.007496252,1.777,0,'LL','POLE',1.275,1.275,1.0,4.18,4.18,1.0,173.07,173.07,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'Intrinsic Charm NLO - Pole masses');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (33,2,'FONLL-C',1,1,'TRN',1.0,1.0,5,5,5,1.5,0.118,91.2,0,0.007496252,1.777,0,'LL','POLE',1.275,1.275,1.0,4.18,4.18,1.0,173.07,173.07,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'Intrinsic Charm NNLO - Pole masses');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (34,1,'FONLL-B',1,1,'TRN',1.0,1.0,5,5,5,1.276,0.118,91.2,0,0.007496252,1.777,0,'LL','POLE',1.275,1.275,1.0,4.18,4.18,1.0,173.07,173.07,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'NLO IC Q0=mc+eps');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (35,1,'FONLL-B',1,1,'TRN',1.0,1.0,5,5,5,1.274,0.118,91.2,0,0.007496252,1.777,0,'LL','POLE',1.275,1.275,1.0,4.18,4.18,1.0,173.07,173.07,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'NLO IC Q0=mc-eps (bline for 34)');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (36,1,'FONLL-B',1,1,'TRN',1.0,1.0,5,5,5,1.2403,0.118,91.2,0,0.007496252,1.777,0,'LL','MSBAR',0.986,3.0,1.0,4.18,4.18,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'NLO IC MSbar Q0=mc(mc)+eps');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (37,1,'FONLL-B',1,1,'TRN',1.0,1.0,5,5,5,1.2401,0.118,91.2,0,0.007496252,1.777,0,'LL','MSBAR',0.986,3.0,1.0,4.18,4.18,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'NLO IC MSbar Q0=mc(mc)-eps (bline for 36)');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (38,1,'FONLL-B',1,1,'TRN',1.0,1.0,5,5,5,1.11,0.118,91.2,0,0.007496252,1.777,0,'LL','MSBAR',1.275,1.275,1.0,4.18,4.18,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'Final IC NLO - MSbar Central mc baseline');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (39,1,'FONLL-B',1,1,'TRN',1.0,1.0,5,5,5,1.11,0.118,91.2,0,0.007496252,1.777,0,'LL','MSBAR',1.15,1.15,1.0,4.18,4.18,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'Final IC NLO - MSbar Lower mc baseline');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (40,1,'FONLL-B',1,1,'TRN',1.0,1.0,5,5,5,1.11,0.118,91.2,0,0.007496252,1.777,0,'LL','MSBAR',1.4,1.4,1.0,4.18,4.18,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'Final IC NLO - MSbar Upper mc baseline');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (41,1,'FONLL-B',1,1,'TRN',1.0,1.0,5,5,5,1.65,0.118,91.2,0,0.007496252,1.777,0,'LL','MSBAR',1.275,1.275,1.0,4.18,4.18,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'Final IC NLO - MSbar Central mc FC');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (42,1,'FONLL-B',1,1,'TRN',1.0,1.0,5,5,5,1.65,0.118,91.2,0,0.007496252,1.777,0,'LL','MSBAR',1.15,1.15,1.0,4.18,4.18,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'Final IC NLO - MSbar Lower mc FC');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (43,1,'FONLL-B',1,1,'TRN',1.0,1.0,5,5,5,1.65,0.118,91.2,0,0.007496252,1.777,0,'LL','MSBAR',1.4,1.4,1.0,4.18,4.18,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'Final IC NLO - MSbar Upper mc FC');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (44,1,'FONLL-B',1,1,'TRN',1.0,1.0,5,5,5,1.11,0.118,91.2,0,0.007496252,1.777,0,'LL','POLE',1.47,1.47,1.0,4.18,4.18,1.0,173.07,173.07,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'Final IC NLO - POLE baseline');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (45,1,'FONLL-B',1,1,'TRN',1.0,1.0,5,5,5,1.65,0.118,91.2,0,0.007496252,1.777,0,'LL','POLE',1.47,1.47,1.0,4.18,4.18,1.0,173.07,173.07,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'Final IC NLO - POLE FC');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (46,1,'FONLL-B',0,0,'TRN',1.0,1.0,5,5,5,1.65,0.118,91.2,0,0.007496252,1.777,0,'LL','MSBAR',1.275,1.275,1.0,4.18,4.18,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'Final IC NLO - MSbar FC dIC off DAMP off');
INSERT INTO `TheoryIndex` (ID,PTO,FNS,DAMP,IC,ModEv,XIR,XIF,NfFF,MaxNfAs,MaxNfPdf,Q0,alphas,Qref,QED,alphaqed,Qedref,SxRes,SxOrd,HQ,mc,Qmc,kcThr,mb,Qmb,kbThr,mt,Qmt,ktThr,CKM,MZ,MW,GF,SIN2TW,TMC,MP,Comments) VALUES (47,1,'FONLL-B',1,0,'TRN',1.0,1.0,5,5,5,1.65,0.118,91.2,0,0.007496252,1.777,0,'LL','MSBAR',1.275,1.275,1.0,4.18,4.18,1.0,162.7,162.7,1.0,'0.97428 0.22530 0.003470 0.22520 0.97345 0.041000 0.00862 0.04030 0.999152',91.1876,80.398,1.1663787e-05,0.23126,1,0.938,'Final IC NLO - MSbar FC dIC off DAMP on');

COMMIT;
