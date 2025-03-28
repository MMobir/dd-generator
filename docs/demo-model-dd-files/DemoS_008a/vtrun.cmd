@echo off
SET "$case_name=demos_008a"
SET "$vd_file_name=demos_008a_1103"
Title demos_008a [ Demo Step 008 ELC and TRA CO2 Bounds ] [DEMOS_008A] 
CALL ..\..\..\GAMS_SrcTIMES.v4.5.4\VT_GAMS %$case_name% ..\..\GAMS_SrcTIMES.v4.5.4 GAMSSAVE\%$case_name% '' ..\ lo=1 2>&1 | tee "%$case_name%_run_log.txt"
GDX2VEDA GAMSSAVE\%$case_name% ..\..\..\GAMS_SrcTIMES.v4.5.4\times2veda.vdd %$vd_file_name%
@echo Closed >RunTerminated
