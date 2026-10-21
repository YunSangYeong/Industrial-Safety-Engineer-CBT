import { describe, expect, it } from 'vitest';
import { answerExam, BASE_BANK as bank, checkPractice, createExam, emptyStore, fingerprint, grade, importQuestions, nextPractice, parseCsv, remainingSeconds, restoreStore, startPractice, SUBJECTS, submitExam, validateQuestion } from '../src/model';
import { QUALIFICATION as rules } from '../src/qualification';

describe('산업안전기사 문제은행과 시험', () => {
  it('1000개 고유 문항, 120개 개념, 24개 유형의 880개 숫자 변형', () => {
    expect(bank).toHaveLength(1000);
    expect(new Set(bank.map(q => q.id)).size).toBe(1000);
    expect(new Set(bank.map(fingerprint)).size).toBe(1000);
    expect(bank.filter(q => !q.family)).toHaveLength(120);
    expect(new Set(bank.filter(q => q.family).map(q => q.family)).size).toBe(24);
    expect(SUBJECTS.map(s => bank.filter(q => q.subject === s).length)).toEqual([168,168,168,168,164,164]);
    bank.forEach(q => { expect(() => validateQuestion(q)).not.toThrow(); expect(q.year).toBeNull(); expect(q.session).toBeNull(); expect(q.type).toBe('original'); expect(q.explanation.length).toBeGreaterThan(30); });
  });
  it('6과목 각20개, 총120개, 180분, 대기 문항 제외', () => {
    const exam=createExam([...bank,{...bank[0],id:'PENDING',verificationStatus:'pending'}], 'main', 1000);
    expect(exam.questions).toHaveLength(120);
    expect(new Set(exam.questions.map(q=>q.id)).size).toBe(120);
    expect(SUBJECTS.map(s=>exam.questions.filter(q=>q.subject===s).length)).toEqual([20,20,20,20,20,20]);
    expect(exam.deadline).toBe(10801000);
    expect(exam.questions.some(q=>q.id==='PENDING')).toBe(false);
    expect(() => createExam(bank.filter(q=>q.subject!==SUBJECTS[0]), 'main')).toThrow();
  });
  function examWithCounts(counts:number[]) {
    const exam=createExam(bank,'main');
    SUBJECTS.forEach((s,i)=>exam.questions.filter(q=>q.subject===s).slice(0,counts[i]).forEach(q=>{exam.answers[q.id]=q.answer;}));
    return exam;
  }
  it('71개 불합격, 72개 평균60점 합격, 과목별8개(40점) 경계', () => {
    expect(grade(examWithCounts([11,12,12,12,12,12])).passed).toBe(false);
    expect(grade(examWithCounts([12,12,12,12,12,12]))).toMatchObject({score:60,passed:true,unanswered:48});
    expect(grade(examWithCounts([8,12,12,12,14,14])).passed).toBe(true);
    expect(grade(examWithCounts([7,20,20,20,20,20])).passed).toBe(false);
    expect(grade(examWithCounts([0,20,20,20,20,20])).score).toBe(83.3);
    expect(grade(examWithCounts([0,20,20,20,20,20])).passed).toBe(false);
  });
  it('가족별 우선 추출, 부족하면 고유 ID 보충', () => {
    for(let i=0;i<10;i++){
      const e=createExam(bank,'main');
      const families=e.questions.filter(q=>q.family).map(q=>q.family);
      expect(new Set(families).size).toBe(families.length);
    }
    expect(createExam(bank.map(q=>({...q,family:q.subject})),'main').questions).toHaveLength(120);
  });
  it('답안 변경, 만료 후 변경 금지, 중복 제출 방지', () => {
    let s={...emptyStore(),exam:createExam(bank,'main',1000)};
    const id=s.exam!.questions[0].id;
    let state=answerExam(s,id,1,2000);state=answerExam(state,id,2,3000);
    expect(state.exam?.answers[id]).toBe(2);
    state=answerExam(state,id,3,10801000);
    expect(state.exam).toBeNull();expect(state.results[0].answers[id]).toBe(2);
    expect(state.results[0].reason).toBe('timeout');expect(state.attempts).toHaveLength(120);
    expect(submitExam(state)).toEqual(state);
  });
  it('새로고침은 절대 시각을 유지하고 잘못된 과목 분포 저장을 거부', () => {
    const state={...emptyStore(),exam:createExam(bank,'main',1000)};
    expect(restoreStore(JSON.stringify(state)).exam?.deadline).toBe(10801000);
    expect(remainingSeconds(state.exam.deadline,1000)).toBe(10800);
    expect(remainingSeconds(state.exam.deadline,10800999)).toBe(1);
    expect(remainingSeconds(state.exam.deadline,10801000)).toBe(0);
    expect(remainingSeconds(state.exam.deadline,99999999)).toBe(0);
    expect(()=>restoreStore('{broken')).toThrow();
    expect(()=>restoreStore(JSON.stringify({...state,exam:{...state.exam,questions:[]}}))).toThrow();
    const altered=structuredClone(state);altered.exam.questions[0].subject=SUBJECTS[0];altered.exam.questions[1].subject=SUBJECTS[0];
    // Force all questions into one subject: the exact distribution must be checked.
    altered.exam.questions.forEach(q=>{q.subject=SUBJECTS[0];});
    expect(()=>restoreStore(JSON.stringify(altered))).toThrow('과목별');
  });
  it('랜덤 순회 중 ID 중복 없음, 1문항 복습도 재진입', () => {
    let p=startPractice(bank,'main',SUBJECTS[0]);const seen=new Set();
    for(let i=0;i<168;i++){expect(seen.has(p.currentId)).toBe(false);seen.add(p.currentId);p=nextPractice(p,bank);}
    p=startPractice(bank,'main','전체',[bank[0].id]);
    expect(nextPractice({...p,revealed:true},bank)).toMatchObject({currentId:bank[0].id,revealed:false});
  });
  it('즉시채점은 한 번만 기록, 정답 복습은 오답에서 제거', () => {
    const q=bank[0];const p=startPractice(bank,'main','전체',[q.id]);
    const state=checkPractice({...emptyStore(),wrongIds:[q.id],practice:{...p,selected:q.answer}},bank);
    expect(state.practice).toMatchObject({revealed:true,streak:1,correct:1,answered:1});
    expect(state.wrongIds).toEqual([]);expect(state.attempts).toHaveLength(1);
    expect(checkPractice(state,bank)).toEqual(state);
  });
});

describe('가져오기·원자성·보존',()=>{
  const custom={...bank[0],id:'CUSTOM-001',question:'사용자가 직접 작성한 안전교육 검토 문항'};
  it('로컬 가져오기는 대기, ID·보기 재배치 중복 제거',()=>{
    expect(importQuestions([custom],bank).added[0].verificationStatus).toBe('pending');
    expect(importQuestions([bank[0],{...bank[0],id:'OTHER',choices:[...bank[0].choices].reverse(),answer:5-bank[0].answer}],bank)).toMatchObject({added:[],duplicates:2});
  });
  it('잘못된 답·보기·연도·URL·과목을 거부',()=>{
    for(const v of [{...custom,answer:5},{...custom,choices:['a','a','b','c']},{...custom,year:2025},{...custom,sourceUrl:'javascript:alert(1)'},{...custom,subject:'전기이론'}]) expect(()=>importQuestions([v],bank)).toThrow();
    expect(()=>importQuestions([custom,{...custom,id:'BAD',answer:99}],bank)).toThrow('2번 문항');
  });
  it('CSV 쉼표·줄바꿈·따옴표 처리, 잘못된 행 거부',()=>{
    expect(parseCsv('id,question\nX,"첫째, 줄\n둘째 ""인용"""')[0]).toMatchObject({id:'X',question:'첫째, 줄\n둘째 "인용"'});
    expect(()=>parseCsv('id,id\nx,x')).toThrow();expect(()=>parseCsv('id,question\n"open')).toThrow();
    expect(()=>parseCsv('id,question\none')).toThrow();
  });
  it('빈 저장소 복원·형식 오류 거부·용량 보존 한도',()=>{
    expect(restoreStore(null)).toEqual(emptyStore());
    expect(restoreStore(JSON.stringify(emptyStore()))).toEqual(emptyStore());
    expect(()=>restoreStore(JSON.stringify({...emptyStore(),practice:{currentId:'bad'}}))).toThrow();
    const q=bank[0];const old={questionId:q.id,subject:q.subject,correct:true,at:1,mode:'practice' as const};
    const p=startPractice(bank,'main','전체',[q.id]);
    const state=checkPractice({...emptyStore(),attempts:Array(5000).fill(old),practice:{...p,selected:q.answer}},bank);
    expect(state.attempts).toHaveLength(5000);expect(rules.storageNamespace).not.toContain('electrician');
  });
});
