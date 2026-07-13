#include <vector>
#include <iostream>

struct CubicSegment {
    double x0; // interval start
    double x1; // interval end
    double a, b, c, d; // coefficients: S(x) = a + b*(x-xc) + c*(x-xc)^2 + d*(x-xc)^3
    double xc; // center of interval
};

// Evaluate cubic at x
double EvalCubicSegment(const CubicSegment& seg, double x){
    double dx = x - seg.xc;
    return seg.a + seg.b*dx + seg.c*dx*dx + seg.d*dx*dx*dx;
}

class PiecewiseCubicSpline {
public:

    std::vector<CubicSegment> _segs;

    const std::vector<CubicSegment> GetSegments(){
        return _segs;
    }

    void SetSegments(const std::vector<CubicSegment>& s){
        _segs = s;
    }


    // default constructor
    PiecewiseCubicSpline() = default;

    PiecewiseCubicSpline(const std::vector<CubicSegment>& s)
    {
        SetSegments(s);
    }

    PiecewiseCubicSpline(const char* file="coeffs_global.txt")
    {
        if (file[0] == '\0') return;

        std::ifstream in(file);
        if(!in.is_open()){
            std::cerr << "Cannot open file: " << file << std::endl;
            return;
        }

        std::string line;
        std::getline(in, line); // skip header

        while(std::getline(in, line)){
            if(line.empty() || line[0]=='#') continue;

            std::istringstream ss(line);

            CubicSegment s;
            ss >> s.xc >> s.x0 >> s.x1
               >> s.a >> s.b >> s.c >> s.d;

            cout << s.xc << endl;

            if(ss.fail()) continue;

            _segs.push_back(s);
        }

        in.close();

        std::cout << "Loaded segments: " << _segs.size() << std::endl;
    }


    double Eval(double x) const {
        if(_segs.empty()) return 0.0;

        // find interval (linear search, same as your code)
        size_t k = 0;
        for(; k < _segs.size(); ++k){
            if(x >= _segs[k].x0 && x <= _segs[k].x1)
                break;
        }

        if(k == _segs.size()) k = _segs.size() - 1;
        return EvalCubicSegment(_segs[k], x);
    }

    double EvalSafe(double x) const {
        if(_segs.empty()) return 0.0;
        if(x <= _segs.front().x0) return EvalCubicSegment(_segs.front(), x);
        if(x >= _segs.back().x1)  return EvalCubicSegment(_segs.back(), x);
        return Eval(x);
    }

    size_t Size() const { return _segs.size(); }
};
