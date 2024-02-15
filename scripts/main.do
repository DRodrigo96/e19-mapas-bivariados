* main.do
* ==================================================
* settings
clear all
global cwd "/path/to/working/directory/e19-mapas-bivariados/"
global a "scripts"
global b "data"
global c "temp"
global d "resources"

cd "$cwd/$b"
quietly {
  foreach x in sumaria-2019 enaho01a-2019-300 {
    unicode analyze "`x'.dta"
    unicode encoding set "ISO-8859-1"
    unicode translate "`x'.dta"
  }
}

clear all
set more off
cd "$cwd"
* --------------------------------------------------

* [NOTE] education
* --------------------------------------------------
use "$b/enaho01a-2019-300.dta", clear
gen year = 2019
order year, first

* [NOTE] indicator: años de educación (a_edu)
replace p301c = 0 if p301a == 3 | p301b ~= . | p301c == .

gen a_edu = 0 if p301a == 1
replace a_edu = 1 if p301a == 2
replace a_edu = p301b + p301c if p301a == 3
replace a_edu = 1 + 6 if p301a == 4
replace a_edu = 1 + 6 + p301b if p301a == 5
replace a_edu = 1 + 6 + 5 if p301a == 6
replace a_edu = 1 + 6 + 5 + p301b if p301a > 6 & p301a < 11
replace a_edu = 1 + 6 + 5 + 5 + p301b if p301a == 11

keep if p204 == 1 // solo miembros de hogar
keep year conglome vivienda hogar ubigeo dominio estrato p207 p208a a_edu factora07 factor07
save "$c/mod300_2019.dta", replace

* [NOTE] sumaria
* --------------------------------------------------
use "$b/sumaria-2019.dta", clear
gen year = 2019
order year, first

* [NOTE] indicator: ingreso monetario neto familiar mensual per cápita (ingm_fampc)
gen ingm_fampc = (ingmo2hd/mieperho)/12

keep year conglome vivienda hogar ubigeo dominio estrato mieperho ingm_fampc pobreza factor07
save "$c/suma_2019.dta", replace

* [NOTE] final dataset (db_final.dta)
* --------------------------------------------------
use "$c/mod300_2019.dta", clear
merge m:1 year conglome vivienda hogar ubigeo dominio estrato using "$c/suma_2019.dta", keepusing(mieperho ingm_fampc pobreza)
keep if _merge == 3
drop _merge

gen dpto = substr(ubigeo,1,2)
gen prov = substr(ubigeo,1,4)
replace prov = prov + "00"

table year [iw = factora07] if p208a >= 18, c(mean a_edu mean ingm_fampc)
table dpto [iw = factora07] if p208a >= 18, c(mean a_edu mean ingm_fampc)

* [NOTE] collapse a nivel provincial (base para Python: db_provincial.csv)
preserve
collapse (mean) a_edu ingm_fampc [iw = factora07] if p208a >= 18, by(prov)
export delimited using "$c/db_provincial.csv", delimiter(";") nolabel replace
restore

save "$c/db_final.dta", replace

* [NOTE] Madre de Dios
use "$c/db_final.dta", clear
table prov [iw = factora07] if dpto == "17", c(mean a_edu mean ingm_fampc)
