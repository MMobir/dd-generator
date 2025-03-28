@echo off
SET "$case_name=vedademoref_multcurr"
SET "$vd_file_name=vedademoref_multcurr_1103"
Title vedademoref_multcurr [ testing multiple currencies on same attribute ] [VEDADEMOREF_MULTCURR] 
CALL ..\..\..\GAMS_SrcTIMES.v4.5.4\VT_GAMS %$case_name% ..\..\GAMS_SrcTIMES.v4.5.4 GAMSSAVE\%$case_name% '' ..\ lo=1 2>&1 | tee "%$case_name%_run_log.txt"
GDX2VEDA GAMSSAVE\%$case_name% ..\..\..\GAMS_SrcTIMES.v4.5.4\times2veda.vdd %$vd_file_name%
@echo Closed >RunTerminated
