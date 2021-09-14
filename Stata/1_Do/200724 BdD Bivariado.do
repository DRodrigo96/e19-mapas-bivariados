


*█ Unicode translate

clear all
set more off

cd "C:\Users\RODRIGO\Desktop\Portafolio Git\6. Gráficos Presentación\1 Mapa Bivariado\Stata\\2_BD"

quietly {
foreach x in sumaria-2019 enaho01a-2019-300 {
unicode analyze "`x'.dta"
unicode encoding set "ISO-8859-1"
unicode translate "`x'.dta"
}
}


*█ Carpeta de trabajo

clear all
set more off

cd "C:\Users\RODRIGO\Desktop\Portafolio Git\6. Gráficos Presentación\1 Mapa Bivariado\Stata\\"

global a "1_Do"
global b "2_BD"
global c "3_Temp"
global d "4_Tables"


*█ EDUCACIÓN *******************************************************************

use "$b\\enaho01a-2019-300.dta", clear
gen year = 2019
order year, first


*█ Indicador: Años de educación (a_edu)

replace p301c = 0 if p301a == 3 | p301b ~= . | p301c == .

gen a_edu = 0 							if p301a == 1
replace a_edu = 1 						if p301a == 2
replace a_edu = p301b + p301c 			if p301a == 3
replace a_edu = 1 + 6 					if p301a == 4
replace a_edu = 1 + 6 + p301b 			if p301a == 5
replace a_edu = 1 + 6 + 5 				if p301a == 6
replace a_edu = 1 + 6 + 5 + p301b 		if p301a > 6 & p301a < 11
replace a_edu = 1 + 6 + 5 + 5 + p301b 	if p301a == 11


*█ Base de datos temporal: Educación (mod300_2019.dta)

keep if p204 == 1 // Solo miembros de hogar
keep year conglome vivienda hogar ubigeo dominio estrato p207 p208a a_edu factora07 factor07
save "$c\\mod300_2019.dta", replace



*█ SUMARIA *********************************************************************

use "$b\\sumaria-2019.dta", clear 
gen year = 2019
order year, first


*█ Indicador: Ingreso monetario neto familiar mensual per cápita (ingM_fampc)

gen ingM_fampc = (ingmo2hd/mieperho)/12


*█ Base de datos temporal: Sumaria 2019 (suma_2019)

keep year conglome vivienda hogar ubigeo dominio estrato mieperho ingM_fampc pobreza factor07
save "$c\\suma_2019.dta", replace



*█ BASE DE DATOS FINAL (BdDFinal.dta) ******************************************

use "$c\\mod300_2019.dta", clear
merge m:1 year conglome vivienda hogar ubigeo dominio estrato using "$c\\suma_2019.dta", keepusing(mieperho ingM_fampc pobreza)
keep if _merge == 3
drop _merge

* Departamentos
gen dpto = substr(ubigeo,1,2)

* Provincias
gen prov = substr(ubigeo,1,4)
replace prov = prov + "00"

* Tabla de indicadores por departamento
table year [iw = factora07] if p208a >= 18, c(mean a_edu mean ingM_fampc)
table dpto [iw = factora07] if p208a >= 18, c(mean a_edu mean ingM_fampc)


*█ Collapse a nivel provincial. Base para Python (BdDProvincial.csv)
preserve
collapse (mean) a_edu ingM_fampc [iw = factora07] if p208a >= 18, by(prov)
export delimited using "$d\\BdDProvincial.csv", delimiter(";") nolabel replace
restore 

save "$c\\BdDFinal.dta", replace

* Madre de Dios 
use "$c\\BdDFinal.dta", clear


table prov [iw = factora07] if dpto == "17", c(mean a_edu mean ingM_fampc)



