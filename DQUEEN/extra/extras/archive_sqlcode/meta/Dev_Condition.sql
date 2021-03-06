/*************************************************************************/
--  Assigment: DataQueen project
--  Description: Running script for Meta Person
--  Author: Junghyun E, Byun
--  Date:  22. May, 2019
--  Job name: Random sampling Original data (EHR)
--  Language: MSSQL
--  Target data: Meta
--  Description
/*************************************************************************/
 select
        ROW_NUMBER() over(order by newid()) AS uniq_num
        ,tm1.*
        ,case
            when tm1.MEDDATE <= dp1.Btdt then 'Y'
            when tm1.visit_time is not null and tm1.visit_time <= dp1.Btdt then 'Y'
            when tm1.dsch_date is not null and tm1.dsch_date < dp1.Btdt then 'Y'
            when tm1.dsch_time is not null and tm1.dsch_time < dp1.Btdt then 'Y'
            else 'N'
         end as Brith_err
        ,dp1.Btdt
        ,case
            when tm1.MEDDATE > dd1.DIEDATE then 'Y'
            when tm1.visit_time is not null and tm1.visit_time > dd1.DIEDATE then 'Y'
            when tm1.dsch_date is not null and tm1.dsch_date > dd1.DIEDATE then 'Y'
            when tm1.dsch_time is not null and tm1.dsch_time > dd1.DIEDATE then 'Y'
            else 'N'
         end as death_err
        ,dd1.DIEDATE
        ,case
            when tm1.MEDDATE > tm1.dsch_date then 'Y'
            when (tm1.visit_time is not null and tm1.dsch_time is not null) and tm1.visit_time > tm1.dsch_time then 'Y'
            else 'N'
         end as date_err

    into Byun_meta_2M.dbo.Dev_Condition
    from
    (select distinct
          'MMPDIAGT' as tbnm
        , m1.PATNO  --환자ID
        , m1.MEDDATE  --진료/입원/수술(DSC)/응급실도착일시
        , v1.visit_time
        , v1.dsch_date
        , v1.dsch_time
        , m1.MEDDEPT  --진료과
        , m1.PATFG  --내원구분
        , m1.CHADR  --주치의
        , m1.SEQNO  --순번
        , m1.DIAGCODE  --진단코드
        , m1.DIAGNAME  --진단명
        , m1.MAINYN  --주진단여부
        , m1.IMPRESSYN  --확정진단여부
        , m1.ADMDIAYN  --입원진단여부
        , m1.DSCDIAYN  --퇴원진단여부
        , m1.REGTIME --등록일시
        , v1.REJTTIME

        from
             (select
                 PATNO, MEDDATE, MEDDEPT, PATFG, CHADR, SEQNO, DIAGCODE, DIAGNAME, EXTCDYN,
                 MAINYN, IMPRESSYN, COMDISYN, ADMDIAYN, DSCDIAYN, REGTIME, OUTYN, POACODE, ACUTYN
              from Byun_origin_Rand_2M.dbo.MMPDIDAGT
                where PATFG in ('O')) as m1
        left join (select
                    patno, visit_date, visit_time, dsch_date, dsch_time, cha_dr, med_dept, REJTTIME
                   from Byun_meta_2M.dbo.Dev_visit_fn_2
                    where PATFG = 'O' and tbnm in ('AOOPDLST')) as v1
                on v1.patno = m1.PATNO and v1.visit_date = m1.MEDDATE and v1.med_dept = m1.MEDDEPT and v1.cha_dr = m1.CHADR


     -- 응급/입원/통원수술
    union all
      select distinct
          'MMPDIAGT' as tbnm
        , m1.PATNO  --환자ID
        , m1.MEDDATE  --진료/입원/수술(DSC)/응급실도착일시
        , v1.visit_time
        , v1.dsch_date
        , v1.dsch_time
        , m1.MEDDEPT  --진료과
        , m1.PATFG  --내원구분
        , m1.CHADR  --주치의
        , m1.SEQNO  --순번
        , m1.DIAGCODE  --진단코드
        , m1.DIAGNAME  --진단명
        , m1.MAINYN  --주진단여부
        , m1.IMPRESSYN  --확정진단여부
        , m1.ADMDIAYN  --입원진단여부
        , m1.DSCDIAYN  --퇴원진단여부
        , m1.REGTIME --등록일시
        , v1.REJTTIME

        from
             (select
                 PATNO, MEDDATE, MEDDEPT, PATFG, CHADR, SEQNO, DIAGCODE, DIAGNAME, EXTCDYN,
                 MAINYN, IMPRESSYN, COMDISYN, ADMDIAYN, DSCDIAYN, REGTIME, OUTYN, POACODE, ACUTYN
              from Byun_origin_Rand_2M.dbo.MMPDIDAGT
                where PATFG in ('E','I','D')) as m1
        left join (select
                    patno, visit_date, visit_time, dsch_date, dsch_time, cha_dr, med_dept, REJTTIME
                   from Byun_meta_2M.dbo.Dev_visit_fn_2
                    where PATFG in ('E', 'I','D') and tbnm in ('APIPDSLT')) as v1
                on v1.patno = m1.PATNO and v1.visit_date = m1.MEDDATE and v1.med_dept = m1.MEDDEPT and v1.cha_dr = m1.CHADR

     --퇴원진단
    union all

         select distinct
              'SMDDIAGT' as tbnm
             ,s1.PATNO  -- 환자ID
             ,a1.visit_date as MEDDATE
             ,a1.visit_time
             ,s1.DSCHDATE as dsch_date -- 퇴원일
             ,a1.dsch_time
             ,s1.DEPTCODE as MEDDEPT  -- 부서코드
             ,a1.patfg
             ,s1.CHADR  -- 주치의
             ,s1.SEQNO  -- 순번
             ,s1.DIAGCODE  -- 진단코드
             ,s1.DIAGNAME
             ,s1.MAINYN  -- 주코드여부
             ,null as IMPRESSYN
             ,null as ADMDIAYN
             , 'O' as DSCDIAYN
             ,s1.REGTIME  -- 생성일시
             ,a1.REJTTIME
        from
             (select
                    PATNO,DSCHDATE,SEQNO,DIAGCODE,DIAGNAME
                    ,DEPTCODE,MAINYN,CHADR,REGTIME  from Byun_origin_Rand_2M.dbo.SMDDIAGT) as s1
         join
                 ( select  patno, patfg,visit_date, visit_time, dsch_date, dsch_time, cha_dr, med_dept, REJTTIME
                   from Byun_meta_2M.dbo.Dev_visit_fn_2
                    where tbnm = 'APIPDSLT' ) as a1
        on s1.PATNO = a1.patno and s1.DEPTCODE = a1.med_dept and CONVERT(VARCHAR, s1.DSCHDATE,23) = CONVERT(VARCHAR, a1.dsch_time,23)

    -- 검진, 산업의학
    union all
        select distinct
             'Gumjin+Sanup' as tbnm
            , m1.PATNO  --환자ID
            , m1.MEDDATE  --진료/입원/수술(DSC)/응급실도착일시
            , v1.visit_time
            , v1.dsch_date
            , v1.dsch_time
            , m1.MEDDEPT  --진료과
            , m1.PATFG  --내원구분
            , m1.CHADR  --주치의
            , m1.SEQNO  --순번
            , m1.DIAGCODE  --진단코드
            , m1.DIAGNAME  --진단명
            , m1.MAINYN  --주진단여부
            , m1.IMPRESSYN  --확정진단여부
            , m1.ADMDIAYN  --입원진단여부
            , m1.DSCDIAYN  --퇴원진단여부
            , m1.REGTIME --등록일시
            , v1.REJTTIME

            from
                 (select
                     PATNO, MEDDATE, MEDDEPT, PATFG, CHADR, SEQNO, DIAGCODE, DIAGNAME, EXTCDYN,
                     MAINYN, IMPRESSYN, COMDISYN, ADMDIAYN, DSCDIAYN, REGTIME, OUTYN, POACODE, ACUTYN
                  from Byun_origin_Rand_2M.dbo.MMPDIDAGT
                    where PATFG in ('G','M')) as m1
            left join (select
                        patno, visit_date, visit_time, dsch_date, dsch_time,cha_dr, med_dept, REJTTIME
                       from Byun_meta_2M.dbo.Dev_visit_fn_2
                        where PATFG in ('G','S')) as v1
                on v1.patno = m1.PATNO and v1.visit_date = m1.MEDDATE ) as tm1
            inner join (select PATNO, Btdt from Byun_meta_2M.dbo.Dev_person) as dp1
                on dp1.PATNO = tm1.PATNO
            left join (select PATNO, DIEDATE from Byun_meta_2M.dbo.Dev_death) as dd1
                on dd1.PATNO = tm1.PATNO

-- [2019-05-22 14:13:05] 23,001,260 rows affected in 1 m 24 s 211 ms



