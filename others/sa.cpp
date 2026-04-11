// https://www.luogu.com.cn/problem/P1337
#include <iostream>
#include <cmath>
#include <iomanip>
#include <utility>
#define rep(i,a,b) for(int i=a;i<=b;i++)
#define per(i,a,b) for(int i=a;i>=b;i--)
using namespace std;

struct node{
    int x,y,w;
};

const int N=1010;

int n;
node a[N];

#define fi first
#define se second
pair<double,double> ans;
double mne;

double f(double x, double y){
    double res = 0;
    rep(i,1,n) res += sqrt((x-a[i].x)*(x-a[i].x)+(y-a[i].y)*(y-a[i].y))*a[i].w;
    return res;
}

void sa(){
    double T = 10000;      // 覆盖题目的坐标范围即可
    double cur_x = ans.fi, cur_y = ans.se; 
    double cur_e = mne;
    
    while(T > 1e-4){       // 精度满足题目 3 位小数要求即可
        double nx = cur_x + (rand()/(double)RAND_MAX*2-1)*T;
        double ny = cur_y + (rand()/(double)RAND_MAX*2-1)*T;
        double ne = f(nx, ny);
        
        if(ne < cur_e){
            cur_x = nx, cur_y = ny, cur_e = ne;
            if(ne < mne){
                ans.fi = nx, ans.se = ny, mne = ne;
            }
        }
        else if(exp((cur_e - ne) / T) > rand()/(double)RAND_MAX){
            cur_x = nx, cur_y = ny, cur_e = ne; 
        }
        T *= 0.996;        // 降温稍微放缓，增加搜索细致度
    }
}

void solve(){
    cin>>n;
    rep(i,1,n){
        cin>>a[i].x>>a[i].y>>a[i].w;
        ans.fi+=a[i].x, ans.se+=a[i].y;
    }
    ans.fi/=n, ans.se/=n;
    mne = f(ans.fi, ans.se);

    while ((double)clock() / CLOCKS_PER_SEC < 0.9) {
        sa();
    }

    cout<<setprecision(3)<<fixed<<ans.fi<<" "<<ans.se<<endl;
}

int main(){
    srand(time(0));
    solve();
    return 0;
}