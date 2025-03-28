@echo off
SET "$case_name=ref_1w"
SET "$vd_file_name=ref_1w_1103"
Title ref_1w [ with TS def 1-week ] [REF_1W] 
CALL ..\..\..\GAMS_SrcTIMES.v4.5.4\VT_GAMS %$case_name% ..\..\GAMS_SrcTIMES.v4.5.4 GAMSSAVE\%$case_name% '' ..\ lo=1 2>&1 | tee "%$case_name%_run_log.txt"
GDX2VEDA GAMSSAVE\%$case_name% ..\..\..\GAMS_SrcTIMES.v4.5.4\times2veda.vdd %$vd_file_name%
@echo Closed >RunTerminated
