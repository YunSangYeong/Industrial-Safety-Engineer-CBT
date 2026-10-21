"""Deterministic original learning questions; no copied past exam content.
Numeric arithmetic is checked separately in tests/bank.test.ts.
No legal thresholds are asserted. Review scope: internal AI review, not expert review.
"""
import ast, csv, hashlib, json, re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SUBJECTS = ast.literal_eval(re.search(r'subjects: (\[.*?\]),', (ROOT/'src/qualification.ts').read_text()).group(1))
SOURCE = 'https://github.com/YunSangYeong/Industrial-Safety-Engineer-CBT/blob/main/docs/QUESTION_BANK.md'
BASE = dict(difficulty='중', year=None, session=None, type='original', sourceUrl=SOURCE,
 verificationStatus='reviewed', reviewNote='AI 자체 작성 후 문장·선택지 내부 검토. 계산형은 별도 TypeScript 수식으로 재계산. 공식 출제기준 대조·외부 전문가 검수 미완료. 저장소 링크는 작성 이력이며 외부 정답 증빙이 아님.', version='main',rights='자체 제작 학습문항 · CC BY 4.0')
questions=[]
concepts=json.loads((ROOT/'scripts/concepts.json').read_text())
for subject, rows in enumerate(concepts):
 assert len(rows)==20
 for i,(topic,stem,correct,*rest) in enumerate(rows):
  distractors,explanation=rest[:3],rest[3]
  choices=[correct,*distractors]; rotate=i%4; choices=choices[rotate:]+choices[:rotate]
  questions.append(dict(BASE,id=f'ISE-C{subject+1}-{i+1:03}',subject=SUBJECTS[subject],topic=topic,question=stem,choices=choices,answer=choices.index(correct)+1,explanation=explanation))
# family, subject index, topic, unit, params(i), question(params), formula, explanation
families=[
 ('frequency',0,'도수율','건/백만 시간',lambda i:[1+i%5,100000+10000*i],lambda a,h:f'학습용 집계에서 재해 건수가 {a}건, 총 근로시간이 {h}시간이다. 재해 건수 ÷ 총 근로시간 × 1,000,000으로 정의한 도수율은?',lambda a,h:Decimal(a)*1000000/Decimal(h),'도수율 = 재해 건수 ÷ 총 근로시간 × 1,000,000. 건수와 시간의 집계 범위가 같다는 가정이다.'),
 ('severity',0,'강도율','일/천 시간',lambda i:[100+10*i,100000+2000*i],lambda d,h:f'학습용 집계에서 근로손실일수 {d}일, 총 근로시간 {h}시간이다. 손실일수 ÷ 근로시간 × 1,000으로 정의한 강도율은?',lambda d,h:Decimal(d)*1000/Decimal(h),'강도율 = 근로손실일수 ÷ 총 근로시간 × 1,000. 주어진 손실일수를 그대로 사용하며 법정 환산일수를 묻는 문제가 아니다.'),
 ('incidence',0,'천인율','명/천 명',lambda i:[1+i%7,200+10*i],lambda a,n:f'재해자 수 {a}명, 평균 근로자 수 {n}명인 학습용 사업장이다. 재해자 수 ÷ 평균 근로자 수 × 1,000으로 정의한 천인율은?',lambda a,n:Decimal(a)*1000/Decimal(n),'천인율 = 재해자 수 ÷ 평균 근로자 수 × 1,000. 분모는 근로시간이 아니라 평균 근로자 수다.'),
 ('completion',0,'개선 이행률','%',lambda i:[20+i,50+i],lambda a,n:f'위험 개선조치 {n}건 중 {a}건을 완료했다. 완료 건수 ÷ 전체 건수 × 100으로 계산한 이행률은?',lambda a,n:Decimal(a)*100/Decimal(n),'이행률 = 완료 건수 ÷ 전체 개선조치 건수 × 100. 이행률만으로 개선 효과까지 입증되는 것은 아니다.'),
 ('series',1,'직렬 신뢰도','%',lambda i:[80+i%19,70+i//2],lambda a,b:f'독립인 두 구성요소의 임무시간 신뢰도가 각각 {a}%, {b}%이다. 둘 다 정상이어야 성공하는 직렬계의 신뢰도는?',lambda a,b:Decimal(a)*Decimal(b)/100,'독립인 직렬계의 신뢰도 R = R₁ × R₂. 백분율을 소수로 바꾸어 곱한 뒤 100을 곱한다. 공통원인 고장은 제외한다.'),
 ('parallel',1,'병렬 신뢰도','%',lambda i:[60+i%19,50+i//2],lambda a,b:f'독립인 두 구성요소의 임무시간 신뢰도가 각각 {a}%, {b}%이다. 어느 하나만 정상이어도 성공하는 병렬계의 신뢰도는?',lambda a,b:100-(Decimal(100-a)*Decimal(100-b)/100),'독립 병렬계는 두 요소가 모두 고장날 때 실패한다. R = 1 − (1−R₁)(1−R₂). 전환 실패와 공통원인 고장은 제외한다.'),
 ('risk',1,'정량 위험 기댓값','건/년',lambda i:[1+i,10+i%8],lambda a,b:f'두 사건이 모두 발생하면 사고가 난다고 가정한다. 첫 사건의 연간 발생확률은 {a}%, 첫 사건 조건에서 둘째 사건 확률은 {b}%다. 연간 한 번의 기회에서 사고 확률을 건/년 기댓값으로 나타내면?',lambda a,b:Decimal(a)*Decimal(b)/10000,'동시 발생확률 = P(A) × P(B|A). 주어진 확률은 %이므로 각각 100으로 나눈다. 연간 한 번의 기회와 사고 최대 한 건이라는 가정이다.'),
 ('rpn',1,'학습용 RPN','점',lambda i:[2+i%8,2+(i//8)%5,1+i%5],lambda a,b,c:f'학습용 FMEA에서 심각도 {a}, 발생도 {b}, 검출도 {c}를 사용한다. 세 평가값의 곱으로 정의한 RPN은?',lambda a,b,c:Decimal(a*b*c),'이 문제에서 정의한 RPN = 심각도 × 발생도 × 검출도. 척도와 우선순위는 조직의 평가 방법에 따라 다르며 법정 기준값이 아니다.'),
 ('stress',2,'인장 응력','MPa',lambda i:[5+i,100+10*i],lambda f,a:f'기계 부재에 축방향 인장력 {f} kN이 작용하고 단면적이 {a} mm²이다. 균일한 인장 응력은? 응력 집중은 무시한다.',lambda f,a:Decimal(f)*1000/Decimal(a),'인장 응력 σ = F/A. 1 kN = 1,000 N, 1 N/mm² = 1 MPa이다. 안전 허용 응력을 판단하는 문제는 아니다.'),
 ('lever',2,'지렛대 평형','N',lambda i:[100+10*i,2+i%5],lambda m,l:f'수직 힘이 작용하는 지렛대가 정적 평형이다. 반대 모멘트가 {m} N·m, 힘의 수직 모멘트팔이 {l} m일 때 필요한 힘은?',lambda m,l:Decimal(m)/Decimal(l),'모멘트 M = F × 수직 모멘트팔 L. 평형에 필요한 힘 F = M/L. 마찰과 지렛대 자중은 제외한다.'),
 ('pressure',2,'유압 압력','MPa',lambda i:[10+i,20+i],lambda f,a:f'유압 피스톤에 힘 {f} kN, 유효 면적 {a} cm²가 주어진다. 압력 손실을 무시한 유체 압력은?',lambda f,a:Decimal(f)*10/Decimal(a),'압력 p = F/A. kN은 1,000 N, cm²는 0.0001 m²이므로 (kN/cm²)×10 = MPa이다.'),
 ('kinetic',2,'운동 에너지','J',lambda i:[20+i,2+i%5],lambda m,v:f'이동하는 기계 부품의 질량은 {m} kg, 속력은 {v} m/s이다. 병진 운동에너지는? 회전 에너지는 제외한다.',lambda m,v:Decimal(m)*v*v/2,'운동에너지 E = ½mv². 질량 kg과 속력 m/s를 사용하면 결과는 J이다. 속력이 두 배면 에너지는 네 배가 된다.'),
 ('shock',3,'접촉 전류','mA',lambda i:[24+i*2,1000+i*100],lambda v,r:f'단순 저항 모델에서 접촉 전압이 {v} V, 경로 저항이 {r} Ω이다. 흐르는 전류는? 인체 안전 한계를 묻는 문제는 아니다.',lambda v,r:Decimal(v)*1000/Decimal(r),'옴의 법칙 I = V/R. 결과 A에 1,000을 곱해 mA로 변환한다. 실제 인체 임피던스는 조건에 따라 달라진다.'),
 ('insulation',3,'절연 누설 모델','μA',lambda i:[100+i*5,2+i%9],lambda v,r:f'전압 {v} V가 저항성 절연 경로 {r} MΩ에 걸린다고 단순화한다. 누설 전류는?',lambda v,r:Decimal(v)/Decimal(r),'I = V/R. MΩ는 10⁶ Ω, μA는 10⁻⁶ A이므로 V를 MΩ 값으로 나누면 μA가 된다. 적합성 기준을 묻지 않는다.'),
 ('joule',3,'전선 발열','J',lambda i:[2+i%5,1+i%7,10+i],lambda a,r,t:f'저항 {r} Ω의 도체에 일정 전류 {a} A가 {t}초 동안 흐른다. 줄열 에너지는? 저항 변화와 열 방출은 무시한다.',lambda a,r,t:Decimal(a*a*r*t),'줄열 Q = I²Rt. A²·Ω·s = J. 전류가 커지면 발열은 전류의 제곱에 비례한다.'),
 ('capacitor',3,'축전 잔류 에너지','J',lambda i:[100+i*20,100+i*5],lambda c,v:f'정전용량 {c} μF인 축전기가 {v} V로 충전되어 있다. 저장 에너지는? 이상적인 축전기로 가정한다.',lambda c,v:Decimal(c)*Decimal('0.000001')*v*v/2,'축전 에너지 E = ½CV². μF를 F로 바꾸기 위해 10⁻⁶을 곱한다. 전원 제거 후에도 에너지가 남을 수 있다.'),
 ('dilution',4,'단순 희석','mg/L',lambda i:[100+i*10,2+i%4,10+i],lambda c,v,vf:f'용질이 반응하지 않고 부피가 가산된다고 가정한다. 농도 {c} mg/L의 용액 {v} L에 깨끗한 용매를 넣어 최종 {vf} L로 만들었다. 최종 농도는?',lambda c,v,vf:Decimal(c)*v/Decimal(vf),'용질 질량 보존 C₁V₁ = C₂V₂. 최종 농도 C₂ = C₁V₁/V₂. 최종 부피를 용매 첨가량과 혼동하지 않는다.'),
 ('ventilation',4,'완전혼합 환기','m³/min',lambda i:[100+i*10,10+i%6],lambda g,c:f'오염물질이 {g} mg/min으로 발생하는 완전혼합 공간이다. 유입 공기 농도 0 mg/m³, 정상상태 목표 농도 {c} mg/m³일 때 이론상 필요한 환기량은? 반응·흡착과 혼합 불완전은 무시한다.',lambda g,c:Decimal(g)/Decimal(c),'정상상태 질량수지 G = Q(C−Cᵢ). 유입 농도 Cᵢ=0이므로 Q = G/C. 실제 설계에는 혼합 효율 등 추가 조건이 필요하다.'),
 ('ppm',4,'체적 농도','ppm',lambda i:[1+i,100+i*10],lambda v,total:f'기체 혼합물의 전체 부피 {total} m³ 중 대상 기체가 {v} L 포함되어 있다. 같은 온도·압력의 이상 혼합물로 가정한 체적 농도는?',lambda v,total:Decimal(v)*1000/Decimal(total),'ppm = 대상 기체 부피 ÷ 전체 부피 × 10⁶. L를 m³로 바꾸는 10⁻³을 적용하면 (L값/m³값)×1,000이다.'),
 ('heat',4,'현열','kJ',lambda i:[2+i,2+i%4,10+i],lambda m,c,t:f'질량 {m} kg, 일정 비열 {c} kJ/(kg·K)인 물질의 온도가 {t} K 증가한다. 상변화와 열손실이 없을 때 필요한 열량은?',lambda m,c,t:Decimal(m*c*t),'현열 Q = mcΔT. kg × kJ/(kg·K) × K = kJ이다. 온도차의 K와 ℃ 크기는 같다.'),
 ('reaction',5,'대칭 보 반력','kN',lambda i:[20+i*2],lambda w:f'자중을 무시하는 수평 단순보의 중앙에 {w} kN의 수직 하중이 작용한다. 좌우 지지는 대칭이다. 한쪽 지점의 수직 반력은?',lambda w:Decimal(w)/2,'대칭과 수직력 평형으로 좌우 반력이 같다. R₁+R₂=W, 따라서 각 반력은 W/2이다. 동하중은 제외한다.'),
 ('bearing',5,'지반 평균 접지압','kPa',lambda i:[100+i*10,2+i%7],lambda f,a:f'총 수직 하중 {f} kN을 수평 받침 면적 {a} m²에 균등하게 전달한다고 가정한다. 평균 접지압은? 실제 지반 허용능력은 별도로 검토한다.',lambda f,a:Decimal(f)/Decimal(a),'평균 접지압 p = 수직 하중/면적. 1 kN/m² = 1 kPa이다. 편심·기초 형상·지반 상태는 별도 검토 대상이다.'),
 ('moment',5,'전도 모멘트','kN·m',lambda i:[5+i,2+i%7],lambda f,h:f'전도 회전점에서 수직 거리 {h} m 위에 수평 힘 {f} kN이 작용한다. 이 힘에 의한 전도 모멘트의 크기는?',lambda f,h:Decimal(f*h),'모멘트 M = 힘 × 힘의 작용선까지의 수직 거리. kN × m = kN·m이다. 전도 안전성 전체 판정은 저항 모멘트 등도 필요하다.'),
 ('slope',5,'경사율','%',lambda i:[1+i%5,10+i],lambda rise,run:f'작업 통로의 수직 높이 차가 {rise} m, 수평 거리가 {run} m이다. 높이 차 ÷ 수평 거리 × 100으로 정의한 경사율은? 적합성 기준을 묻지 않는다.',lambda rise,run:Decimal(rise)*100/Decimal(run),'경사율 = 수직 높이 차/수평 거리 × 100. 수평 거리를 경사면 길이와 혼동하지 않는다. 경사각의 도 단위와 다르다.')
]
for index,(family,s,topic,unit,params,stem,formula,explain) in enumerate(families):
 for i in range(37 if index<16 else 36):
  v=params(i); result=formula(*v).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
  # Nonzero, unique distractors with uniform units; no equivalent answers.
  offsets=[Decimal('1.11'),Decimal('2.22'),Decimal('3.33')]
  choices=[f'{result:.2f} {unit}',*[f'{result+d:.2f} {unit}' for d in offsets]]
  rotate=(i+index)%4;correct=choices[0];choices=choices[rotate:]+choices[:rotate]
  question=stem(*v)+' 소수 셋째 자리에서 반올림하여 둘째 자리까지 표시한다.'
  substitution='입력값: '+', '.join(map(str,v))+f'. 계산 결과 = {result:.2f} {unit}.'
  questions.append(dict(BASE,id=f'ISE-N-{family}-{i+1:03}',subject=SUBJECTS[s],topic=topic,question=question,choices=choices,answer=choices.index(correct)+1,explanation=explain+' '+substitution,family=family,calculation=dict(kind=family,values=v,result=float(result),unit=unit,precision=2)))
assert len(questions)==1000
assert len({q['question'] for q in questions})==1000
out=ROOT/'src/data/questions.json';out.write_text(json.dumps(questions,ensure_ascii=False,indent=2)+'\n')
# Import examples are distinct, pending and not counted in the default bank.
q=dict(questions[0],id='LOCAL-EXAMPLE-001',question='교육 전 실제 작업의 위험을 확인해야 하는 주된 이유는?',choices=['현장 조건에 맞는 예방 내용을 다루기 위해','교재 분량만 늘리기 위해','모든 교육을 없애기 위해','기록을 삭제하기 위해'],answer=1,verificationStatus='pending',reviewNote='등록 양식 예시. 사용자가 출처·해설·정답을 확인한 후 승인해야 함.')
q['explanation']='안전교육은 실제 작업과 위험에 대응해야 한다. 등록 전에는 이 문항의 적용 조건과 정확성을 직접 검토해야 한다.'
p=ROOT/'public/templates';p.mkdir(parents=True,exist_ok=True)
(p/'questions.json').write_text(json.dumps([q],ensure_ascii=False,indent=2)+'\n')
choices=q.pop('choices');q.update({f'choice{i+1}':c for i,c in enumerate(choices)})
with (p/'questions.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(q));writer.writeheader();writer.writerow(q)
print('total',len(questions),'concepts',120,'numeric variants',880,'families',len(families))
print({s:sum(q['subject']==s for q in questions) for s in SUBJECTS})
print('sha256',hashlib.sha256(out.read_bytes()).hexdigest())
