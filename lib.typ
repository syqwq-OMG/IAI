#import "@preview/itemize:0.2.0" as _itemize

#let report(
  name: "syqwq",
  course: "IAI",
  date: datetime.today(),
  tutor: "Tutor",
  id: 10234900421,
  exp-name: "exp name",
  grade: 2024,
  body,
) = {
  set text(font: ("New Computer Modern", "Source Han Serif SC"))

  set page(
    header: box(
      width: 100%,
      stroke: (bottom: luma(200) + .7pt),
      outset: 3pt,
      align(center, text(fill: luma(100))[华东师范大学数据科学与工程学院实验报告]),
    ),
    numbering: "1/1",
  )

  set heading(numbering: "I.1.1")
  set par(justify: true)
  show "。": "."
  show: _itemize.default-enum-list.with(indent: .5em)

  align(center, text(size: 17pt, weight: 600)[华东师范大学数据科学与工程学院实验报告])

  let ti(a, b) = [#strong(a): #b]
  table(
    columns: (1fr,) * 3,
    stroke: luma(220) + .5pt,
    inset: 7pt,
    ti("课程名称", course), ti("年级", grade), ti("上机实践时间", date.display("[year].[month].[day]")),
    ti("指导教师", tutor), ti("姓名", name), [],
    ti("上机实践名称", exp-name), ti("学号", id), [],
  )

  line(length: 100%)


  body
  /*
  = 实验任务

  = 使用环境

  = 实验过程

  = 总结
  */
}

