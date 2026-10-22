const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const element=()=>({querySelector(){return null},querySelectorAll(){return []},scrollTop:0,value:'',textContent:'',innerHTML:'',hidden:false,classList:{add(){},remove(){}},setAttribute(){},focus(){},insertAdjacentHTML(){},addEventListener(){}});
const elements=new Map();const doc={getElementById(id){if(!elements.has(id))elements.set(id,element());return elements.get(id)},addEventListener(){}};
const map={getZoom(){return this.zoom||4},setView(){return this},closePopup(){},fitBounds(){this.fits=(this.fits||0)+1}};
const layer=()=>({addTo(){return this},clearLayers(){},bindPopup(){},bindTooltip(){},on(){},setStyle(style){this.style={...this.style,...style}},bringToFront(){}});
const context=vm.createContext({console,document:doc,L:{map:()=>map,tileLayer:layer,layerGroup:layer,polyline:layer,circleMarker:layer}});
vm.runInContext(fs.readFileSync('assets/app.js','utf8').replace(/loadData\(\);\s*$/,''),context);

context.assert=assert;
context.copiesText=fs.readFileSync('data/map/copies.csv','utf8');
context.stationsText=fs.readFileSync('data/map/stations.csv','utf8');
vm.runInContext(`
state.copies=parseCsv(copiesText).filter(directCopy);
for(const s of parseCsv(stationsText)){if(!state.stationsByCopy.has(s.copy_id))state.stationsByCopy.set(s.copy_id,[]);state.stationsByCopy.get(s.copy_id).push(s)}
for(const a of state.stationsByCopy.values())a.sort((a,b)=>Number(a.source_order)-Number(b.source_order)||Number(a.place_order_within_source)-Number(b.place_order_within_source));
state.copies.forEach(c=>state.selected.add(c.copy_id));
assert.equal(state.copies.length,3394);
for(const c of state.copies) {
 assert.equal(locationAtYear(c.copy_id,2026).station.station_type,'current_holding');
 const birth=stationAnchor(printStation(c.copy_id));
 if(birth!==null)assert.equal(routeAtYear(c.copy_id,birth-1).length,0);
 for(const year of [1450,1500,1600,1800,1950])assert.ok(routeAtYear(c.copy_id,year).every(s=>!s.date_warning&&!excludedDisplayPoint(s)));
 openDetail(c.copy_id);
}
for(const id of ['02129912','02129468','00570345'])assert.ok(!routeAtYear(id,2026).some(s=>Number(s.longitude)>40));
assert.ok(copyStations('02129584').some(s=>s.location_label==='Seefeld'&&!hasPoint(s)));
state.libraries.add('ZurichZB');assert.equal(filteredCopies().length,1609);
state.subjects.add('astronomy');assert.equal(filteredCopies().length,26);
state.subjects.add('Astronomy');assert.equal(filteredCopies().length,30);
state.languages.add('impossible');assert.equal(filteredCopies().length,0);
state.languages.clear();state.subjects.clear();
state.libraries.add('SolothurnZB');assert.equal(filteredCopies().length,2679);
state.libraries.delete('ZurichZB');assert.equal(filteredCopies().length,1070);
state.libraries.clear();assert.equal(filteredCopies().length,3394);
for(const id of ['00201370','00201413']) {openDetail(id);assert.ok(els['detail-content'].innerHTML.includes('No edition reference supplied'));}

state.search='antidotarius';addCheckedMatches();const n=state.savedCopies.size;assert.ok(n>0);
state.search='hortulus';addCheckedMatches();assert.ok(state.savedCopies.size>=n);
state.showSaved=true;state.search='impossible';assert.equal(displayedCopies().length,state.savedCopies.size);
const groups=groupLocations(state.copies,2026);assert.equal(groups.reduce((n,g)=>n+g.entries.size,0),3394);
console.log('PASS: library OR and other-filter AND; 3394 copy details, timeline exclusions, current holdings, Seefeld, Iran conflicts, subject OR / language AND, saved searches.');
`,context);
