import { expect, it } from 'vitest';
import { BASE_BANK } from '../src/model';
// Independent algebraic evaluation. Does not import or call Python generator.
const evaluate:Record<string,(v:number[])=>number>={
 frequency:([n,h])=>n/(h/1e6), severity:([d,h])=>d/(h/1000), incidence:([n,w])=>1000*n/w,
 completion:([done,total])=>100*(1-(total-done)/total),
 series:([r1,r2])=>(r1/100)*(r2/100)*100,
 parallel:([r1,r2])=>r1+r2-r1*r2/100,
 risk:([a,b])=>(a/100)*(b/100),rpn:([s,o,d])=>s*o*d,
 stress:([f,a])=>f/(a/1000),lever:([m,l])=>m/l,pressure:([f,a])=>(f*1000/(a/10000))/1e6,
 kinetic:([m,v])=>m*v**2/2,shock:([v,r])=>v/r*1e3,insulation:([v,r])=>(v/(r*1e6))*1e6,
 joule:([i,r,t])=>(i*r)*i*t,capacitor:([c,v])=>(c*1e-6*v)*v/2,
 dilution:([c,initial,final])=>(c*initial)/final,ventilation:([g,c])=>g/(c-0),ppm:([v,total])=>(v/1000)/total*1e6,
 heat:([m,c,dt])=>m*(c*dt),reaction:([w])=>w-w/2,bearing:([f,a])=>(f*1000/a)/1000,moment:([f,h])=>h*f,slope:([rise,run])=>rise/(run/100)
};
for(const q of BASE_BANK.filter(q=>q.calculation)) it(`독립 재계산·단위·정답·동치 보기: ${q.id}`,()=>{
 const c=q.calculation!;const raw=evaluate[c.kind](c.values);
 const rounded=Math.round((raw+Number.EPSILON*Math.max(1,Math.abs(raw)))*100)/100;
 expect(c.result).toBeCloseTo(rounded,8);
 expect(q.choices[q.answer-1]).toBe(`${rounded.toFixed(2)} ${c.unit}`);
 const equivalent=q.choices.filter(choice=>Math.abs(parseFloat(choice)-rounded)<1e-8);
 expect(equivalent).toHaveLength(1);expect(new Set(q.choices).size).toBe(4);
 expect(q.explanation).toContain(c.unit);
});
