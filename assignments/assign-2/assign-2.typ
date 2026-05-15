#import "../../lib.typ": *

#show: report.with(name: "孙育泉", course: "AI基础", exp-name: "作业2", tutor: "杨彬")

#problem[
  写出复合命题 $(p or not q) to (p and q)$ 的真值表.
]


#solution[
  #let t="T"
  #let f="F"
  #let x=""
  #figure(
    table(
      columns: 6,
      table.header($p$, $q$, $not q$, $p or not q$, $p and q$, $(p or not q) to (p and q)$),
      f,f,t,t,f,f,
      f,t,f,f,f,t,
      t,f,t,t,f,f,
      t,t,f,t,t,t
    )
  )
]

#problem[
  给定知识库中的句子
  $
    & P to Q, \
    & Q to R, \
    & P.
  $
  使用Modus Ponens推理规则证明 $R$.
]

#solution()[
  #enum.item[
    已知 $P$ 和 $P to Q$，根据Modus Ponens推理规则，我们可以得出 $Q$。
  ]

  #enum.item[
    已知 $Q$ 和 $Q to R$，根据Modus Ponens推理规则，我们可以得出 $R$。
  ]
]

#problem(title: [全称量词和存在量词的应用])[
  使用一阶逻辑的全称量词和存在量词来表达下面两个句子：
  + 所有的国王都是富有的

  + 有些国王是富有的
]

#let kin = "King"
#let ric = "Rich"
#let cha = "Charles"

#solution()[
  #enum.item[
    "所有的国王都是富有的" 可以用全称量词表达为：
    $
      forall x, kin(x) => ric(x)
    $
    其中 $kin(x)$ 表示 $x$ 是国王，$ric(x)$ 表示 $x$ 是富有的。
  ]

  #enum.item[
    "有些国王是富有的" 可以用存在量词表达为：
    $
      exists x, kin(x) and ric(x)
    $
    其中 $kin(x)$ 表示 $x$ 是国王，$ric(x)$ 表示 $x$ 是富有的。
  ]
]

#problem(title: [等词应用])[
  等词用于表达两个项指代同一对象或不同对象（加否定词时表示两个项不是同一个对象）

  + Richard至少有两个兄弟

  + Richard有两个兄弟 $x$ 和 $y$
]

#let brother = "Brother"
#let Richard = "Richard"

#solution()[
  #enum.item[
    "Richard至少有两个兄弟" 可以用等词表达为：
    $
      exists x, exists y, (brother(x, Richard) and brother(y, Richard) and x != y)
    $
    其中 $brother(x, Richard)$ 表示 $x$ 是 Richard 的兄弟，$x != y$ 表示 $x$ 和 $y$ 不是同一个对象。
  ]

  #enum.item[
    "Richard有两个兄弟 $x$ 和 $y$" 可以用等词表达为：
    $
      exists x, exists y,
      (
        brother(x, Richard) and brother(y, Richard) and x != y 
        and \
        forall z(
          (brother(z, Richard) => (z = x or z = y))
        )
      )
    $
  ]
]


#problem(title: [推理 ])[
  前向链接和后向链接，从已知事实推导出新事实。

  #enum.item[
    已知知识库中有以下信息：
    $
      & forall x, kin(x) => ric(x) \
      & kin(cha)
    $
    使用前向链接推理出查尔斯是富有的。
  ]

  #enum.item[
    在A国家，任何违反环境保护法的行为都被视为犯罪行为。未经授权倾倒有毒废物至环境中是违法的。如果企业能证明其行为是为了防止更大的环境灾害，可以申请倾倒有毒废物的紧急授权。

    其中某湖泊被政府指定为自然保护区。企业家E在该湖泊中倾倒了有毒废物。E声称其行为是为了防止更严重的环境灾害。此外，没有证据直接表明E申请了紧急授权。

    使用逻辑推理，分析E是否犯了罪。
  ]

]

#solution()[
  #enum.item()[
    根据前向链接推理规则，从 $forall x, kin(x) => ric(x)$ 和 $kin(cha)$，我们可以得出 $ric(cha)$，即查尔斯是富有的。
  ]
  #enum.item[
    设违反环境保护法的行为为 $D(x)$，犯罪行为为 $C(x)$，未经授权倾倒有毒废物为 $P(x)$，申请紧急授权为 $A(x)$。
    根据题意，我们有以下逻辑表达式：
    $
      & forall x, D(x) => C(x) \
      & forall x, (P(x) and not A(x)) => D(x) \
      & P(E) \
      &not A(E)
    $
    
    根据前向链接推理规则，从 $P(E)$ 和 $not A(E)$，我们可以得出 $D(E)$，进而得出 $C(E)$，即E犯了罪。
]
]