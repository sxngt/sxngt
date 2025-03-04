<div align=center>
  
![](https://camo.githubusercontent.com/435a405e1d3b76de77d08aeb83e6f7c80b2b9a269ddb0269b396c4e4a645126d/68747470733a2f2f6d626c6f677468756d622d7068696e662e707374617469632e6e65742f4d6a41794d6a41354d5442664d5455332f4d4441784e6a59794f4445324e7a45324e7a59312e4f4f584c476c594d7156476a354a7a5f4352397a767941766c61395a3431487157495965756248576d3845672e596f4c755251726359595662516f4c304534382d6a6d7464706b6a766d5f4c7a6667585938496a4863626b672e4749462e675f6d696e6e2f63656636633363333462376166616262316338333464653361306434303237322e6769663f747970653d77383030)

ʕ ̳• · • ̳ʔ 상티 깃헙에 오신걸 환영함다 ʕ๑•̀ᴗ-ʔ

#### I am sxngt, a researcher who values and pursues the intersection between engineering philosophy and research philosophy

  <div align=left>
  
## Work Experience
2021 - 2022 / ARSS - MSC (MPTCP Service Commercialization) - SWE<br>
2021 - 2023 / INJE Medical LAB - Researcher<br>
2023        / Always Yoga - Parttime SWE<br>
2023 - 2024 / MITS LAB - Research Intern<br>

## Currently working at 
Team Exhibition BE SWE<br>
Inje SC Lab - Master's program<br>

## Papers
  COVID-19 related SNS crawling - NLP topic modeling, sentiment analysis paper / SCI-indexed journals (IF =4.0)
  <a href="https://www.frontiersin.org/journals/medicine/articles/10.3389/fmed.2022.948917/full">
    [paper]
  </a><br>
  Academic guidance for paper writing on natural language analysis of COVID-related depression and obesity keywords
  <a href="https://www.frontiersin.org/journals/public-health/articles/10.3389/fpubh.2022.894266/full">
    [paper]
  </a><br>


# Tech Stack

```prisma
model Sxngt {
  github    String @default("sxngt")
  email     String @default("sxngt@icloud.com")
  threads   String @default("sang._.hn")
  student   String @default("SC lab AI/Robotics")
  languages String[] @default(["Go", "Rust", "Python", "TS", "Java"])

  model TechStack {
    backend   String[]
    infra     String[]
    database  String[]
    ai_ml     String[]
  }

  techStack TechStack[] @default(
      [
        TechStack(
          backend   = ["SpringBoot", "FastAPI", "NestJS", "Fiber"],
          infra     = ["Docker", "Docker Swarm", "CircleCI", "AWS", "Nginx"],
          database  = ["PostgreSQL", "MongoDB", "Redis"],
          ai_ml     = ["Perfect", "MLflow", "Tensorflow", "TensorRT", "ONNX"]
        )
      ]
    )
}
```
  
<div align=center>
  
## CARDS
  <a href="https://solved.ac/profile/injefol"><img src="https://github-readme-solvedac-hyp3rflow.vercel.app/api/?handle=injefol"/></a>
  <a href="https://github.com/devxb/gitanimals">
    <img src="https://render.gitanimals.org/farms/sxngt"/>
  </a>
