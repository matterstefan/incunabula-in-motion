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
context.pilot=JSON.parse(fs.readFileSync('data/map/marc-pilot.json','utf8'));
vm.runInContext(`
const mei=parseCsv(copiesText).filter(directCopy), marc=adaptMarcPilot(pilot);
state.copies=[...mei,...marc.copies];
for(const s of [...parseCsv(stationsText),...marc.stations]){if(!state.stationsByCopy.has(s.copy_id))state.stationsByCopy.set(s.copy_id,[]);state.stationsByCopy.get(s.copy_id).push(s)}
for(const ss of state.stationsByCopy.values())ss.sort((a,b)=>Number(a.source_order)-Number(b.source_order));
assert.equal(marc.copies.length,31);assert.equal(marc.stations.length,93);
assert.equal(new Set(state.copies.map(c=>c.copy_id)).size,state.copies.length);
assert.equal(filteredCopies().length,3394);
state.collections.add('marc');assert.equal(filteredCopies().length,3425);
state.collections.delete('core');assert.equal(filteredCopies().length,31);
state.libraries.add('SolothurnZB');assert.equal(filteredCopies().length,0);state.libraries.clear();
state.subjects.add('liturgy');assert.equal(filteredCopies().length,0);state.subjects.clear();
for(const c of marc.copies){
 const ss=copyStations(c.copy_id),birth=stationAnchor(ss[0]),event=stationAnchor(ss[1]);
 assert.equal(compactStationsForDisplay(c.copy_id).length,3);
 assert.equal(locationAtYear(c.copy_id,birth-1),null);
 assert.equal(locationAtYear(c.copy_id,event-1).station.station_type,'print_place');
 assert.equal(locationAtYear(c.copy_id,event).station.station_type,'provenance_place');
 assert.equal(locationAtYear(c.copy_id,2026).station.station_type,'current_holding');
 assert.equal(routeAtYear(c.copy_id,event).length,2);
 openDetail(c.copy_id);
 const html=els['detail-content'].innerHTML;
 assert.ok(html.includes('swisscollections '+c.catalogue_id));
 assert.ok(html.includes('MARC '+pilot.find(r=>r.reference_id===c.copy_id).stations[1].evidence[0].tag));
 assert.ok(!html.includes('<dt>MEI</dt>'));
 assert.ok(html.includes('not a complete provenance sequence'));
 assert.ok(html.includes(stationTime(ss[1])));
 state.search=c.catalogue_id;assert.equal(filteredCopies().length,1);state.search='';
 state.languages.add(c.language);assert.ok(filteredCopies().some(x=>x.copy_id===c.copy_id));state.languages.clear();
 state.places.add(filterPlaceLabel(ss[0]));assert.ok(filteredCopies().some(x=>x.copy_id===c.copy_id));state.places.clear();
}
assert.equal(marc.stations.filter(s=>s.display_uncertainty).length,3);
assert.throws(()=>adaptMarcPilot([...pilot,pilot[0]]),/Duplicate/);
state.collections.clear();assert.equal(filteredCopies().length,0);
console.log('PASS: 31 MARC references, 93 stations, dataset/library/subject/language/place filters, IDs, detail sources and timeline qualifications.');
`,context);
