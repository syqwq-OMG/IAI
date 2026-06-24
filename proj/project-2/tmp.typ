#import "@preview/physica:0.9.8":*

$
G=lr({g_i})_(i=1) ^(N), g_i = (s_i, e_i, t_i), G_e=lr({g_i in G mid(|) e_i=e})
$

$
P=lr({p_j})_(j=1) ^(M), p_j=(hat(s_j), hat(e_j), hat(t_j), c_j), P_e=lr({p_j in P mid(|) hat(e_j)=e})
$

$
(hat(s_j)=s_i) and (hat(e_j)=e_i) and (abs(hat(t_j)-t_i)<=tau) => p_j -> "TP"
$

$
c_1>=c_2>=dots.h.c>=c_M
$


$
forall g_i in G, g_i "can be matched at most once"
$

$
"TP"(k)=sum_(j=1)^(k) II(p_j -> "TP"), "FP"(k)=sum_(j=1)^(k) II(p_j -> "FP"), \
"Precision"(k) = frac("TP"(k), "TP"(k)+"FP"(k)), "Recall"(k) = frac("TP"(k), abs(G_e))
$

$
"AP"(e,tau)&=integral_(0) ^(1) "Prec"_e (r;tau) dd(r)\
&= sum_(k=1)^(M) ["Recall"(k)-"Recall"(k-1)] dot max_(tilde(k)>=k) "Precision"(tilde(k))
$

$
cal(E)=lr({"onset", "wakeup"}), cal(T)={12,36,60, dots.h.c, 360} \
"Score" = frac(1, abs(cal(E))dot abs(cal(T))) sum_(e in cal(E)) sum_(tau in cal(T)) "AP"(e,tau)
$


$
y(t)=vb(w)^TT exp(-frac((t-t_0)^(2) , 2vb(sigma)^(2)))
$

$
cal(L)_("CE") = -[y log(p) + (1-y) log(1-p)] 
$

$
cal(L)_("Focal") &= - [alpha y (1-p)^(gamma) log(p) + (1-alpha)(1-y)p^(gamma) log(1-p)] 
$

$
cal(L)&=cal(L)_("event")+lambda_1 cal(L)_("sleep")+lambda_2 cal(L)_("boundary") \
cal(L)_("event")&=cal(L)_("onset")+ cal(L)_("wakeup")   
$

$
cal(L)_("sleep")=frac(
  sum_(b=1)^(B) sum_(t=1)^(T) m_(b,t)^("sl") cal(L)_("CE")(sigma(z_(b,t)^("sl")), y_(b,t)^("sl") ),
   max(sum_(b=1)^(B) sum_(t=1)^(T) m_(b,t)^("sl"), 1)
), m_(b,t)^("sl") in lr({0,1})  
$

$
cal(L)_("boundary")=frac(sum_(b=1)^(B) sum_(t=2)^(T) m_(b,t)^("valid") dot "ReLU"(abs(p_(b,t)^("sl")-p_(b,t-1)^("sl")    )-max(p_(b,t)^("on"), p_(b,t)^("wu")))  ,max(sum_(b=1)^(B) sum_(t=2)^(T) m_(b,t)^("valid"), 1)), m_(b,t)^("valid") in lr({0,1})
$

$
z_(b,t) ^("onset") \
z_(b,t)^("wakeup") \
z_(b,t)^("sleep") \
z_(b,t)^("invalid")
$

$
s_e(t)=alpha tilde(p_e)(t)+(1-alpha) "Mass"_(e)(t) - beta p_("invalid")(t)  
$

#table(
 columns:4,
 stroke:none,
 table.hline(stroke:2pt),
 [实验], [Private], [Public], [结论],
 table.hline(stroke:1pt),
 [small first run], [0.411], [0.363], [跑通 baseline],
  [medium plus 2 fold], [0.605], [0.534], [最佳稳定版本],
  [large 2 fold], [0.552], [0.484], [大模型没有提升],
  [medium plus 3 model ensemble], [0.597], [0.517], [简单融合无效],
  [event plus focal loss], [0.597], [0.543], [Public 提升，Private 略降],
  table.hline(stroke:2pt)
)
// 实验	Private	Public	结论
// small first run	0.411	0.363	跑通 baseline
// medium plus 2 fold	0.605	0.534	最佳稳定版本
// large 2 fold	0.552	0.484	大模型没有提升
// medium plus 3 model ensemble	0.597	0.517	简单融合无效
// event plus focal loss	0.597	0.543	Public 提升，Private 略降