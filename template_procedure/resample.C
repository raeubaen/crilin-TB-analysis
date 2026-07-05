#include <TGraph.h>
#include <TObject.h>
#include <TGraphErrors.h>
#include <TCanvas.h>
#include <vector>
#include <iostream>
#include <fstream>
#include <Eigen/Dense>
#include "PieceWiseCubicSpline.h"
#include <TProfile.h>

TGraphErrors* ProfileToGraph(TProfile* p) {
    int n = p->GetNbinsX();
    auto g = new TGraphErrors(n);
    for (int i = 1; i <= n; ++i) {
        double x  = p->GetBinCenter(i);
        double y  = p->GetBinContent(i);
        double ex = p->GetBinWidth(i) / 2.0;  // or 0
        double ey = p->GetBinError(i);
        g->SetPoint(i-1, x, y);
        g->SetPointError(i-1, ex, ey);
    }
    return g;
}


// Main function
void resample(
    TGraphErrors* gr,
    int detID,
    double dt=6.25,
    const char* outFile="coeffs",
    bool doPlot=false
){
    if(!gr) return;
    size_t Npts = gr->GetN();
    std::vector<double> xMeasured(Npts), yMeasured(Npts), yErr(Npts);
    for(size_t i=0;i<Npts;++i){
        xMeasured[i] = gr->GetX()[i];
        yMeasured[i] = gr->GetY()[i];
        yErr[i] = (gr->GetEY()[i]>0)? gr->GetEY()[i] : 1.0;
    }

    // Sample points
    double tMin = xMeasured.front();
    double tMax = xMeasured.back();
    std::vector<double> tSamples;
    for(double t=tMin; t<tMax; t+=dt) tSamples.push_back(t);
    size_t Nint = tSamples.size();
    cout << "intervals: " << Nint << endl;

    // Intervals centered on sampled points
    std::vector<double> x0(Nint), x1(Nint), xc(Nint);
    for(size_t i=0;i<Nint;++i){
        xc[i] = tSamples[i];
        x0[i] = (i==0)? tMin : (xc[i]-dt/2);
        x1[i] = (i==Nint-1)? tMax : (xc[i]+dt/2);
    }

    // Count total unknowns: 4 coefficients per interval
    size_t Ncoef = 4*Nint;
    Eigen::MatrixXd A = Eigen::MatrixXd::Zero(Ncoef, Ncoef);
    Eigen::VectorXd b = Eigen::VectorXd::Zero(Ncoef);

    // Build weighted LS for each interval independently, then assemble globally
    for(size_t i=0;i<Nint;++i){
        // Measured points in interval
        std::vector<size_t> idx;
        for(size_t j=0;j<Npts;++j){
            if(xMeasured[j]>=x0[i] && xMeasured[j]<=x1[i]) idx.push_back(j);
        }
        for(size_t k=0;k<idx.size();++k){
            size_t j = idx[k];
            double dx = xMeasured[j] - xc[i];
            double w = 1.0/(yErr[j]*yErr[j]+1e-12);

            // Map to global coefficient indices
            size_t base = i*4;
            Eigen::VectorXd row = Eigen::VectorXd::Zero(Ncoef);
            row(base+0) = 1;
            row(base+1) = dx;
            row(base+2) = dx*dx;
            row(base+3) = dx*dx*dx;

            A += w*row*row.transpose();
            b += w*row*yMeasured[j];
        }
    }

    // Continuity constraints: value + derivative
    std::vector<Eigen::VectorXd> Crows;
    std::vector<double> dvals;
    for(size_t i=0;i<Nint-1;++i){
        double xb = x1[i];
        double dx1 = xb - xc[i];
        double dx2 = xb - xc[i+1];

        // 1) Value continuity
        Eigen::VectorXd rowVal = Eigen::VectorXd::Zero(Ncoef);
        rowVal(i*4+0) = 1;
        rowVal(i*4+1) = dx1;
        rowVal(i*4+2) = dx1*dx1;
        rowVal(i*4+3) = dx1*dx1*dx1;

        rowVal((i+1)*4+0) = -1;
        rowVal((i+1)*4+1) = -dx2;
        rowVal((i+1)*4+2) = -dx2*dx2;
        rowVal((i+1)*4+3) = -dx2*dx2*dx2;

        Crows.push_back(rowVal);
        dvals.push_back(0.0);

        // 2) Derivative continuity
        Eigen::VectorXd rowDer = Eigen::VectorXd::Zero(Ncoef);
        rowDer(i*4+1) = 1;          // b_i
        rowDer(i*4+2) = 2*dx1;      // c_i
        rowDer(i*4+3) = 3*dx1*dx1;  // d_i

        rowDer((i+1)*4+1) = -1;         // -b_{i+1}
        rowDer((i+1)*4+2) = -2*dx2;     // -c_{i+1}
        rowDer((i+1)*4+3) = -3*dx2*dx2; // -d_{i+1}

        Crows.push_back(rowDer);
        dvals.push_back(0.0);
    }

    // Assemble augmented system with Lagrange multipliers
    size_t Nconstr = Crows.size(); // previously Nint-1, now 2*(Nint-1)
    Eigen::MatrixXd K = Eigen::MatrixXd::Zero(Ncoef+Nconstr, Ncoef+Nconstr);
    Eigen::VectorXd rhs = Eigen::VectorXd::Zero(Ncoef+Nconstr);

    K.topLeftCorner(Ncoef,Ncoef) = A;
    rhs.head(Ncoef) = b;
    for(size_t i=0;i<Nconstr;++i){
        // bottom-left: constraint row (row Ncoef+i)
        K.block(Ncoef+i, 0, 1, Ncoef) = Crows[i].transpose();

        // top-right: constraint column for Lagrange multipliers
        K.block(0, Ncoef, Ncoef, Nconstr).col(i) = Crows[i];

        // multiplier diagonal
        K(Ncoef+i, Ncoef+i) = 0;

        // RHS
        rhs(Ncoef+i) = dvals[i];
    }
    // Solve
    Eigen::VectorXd sol = K.ldlt().solve(rhs);

    // Extract segments
    std::vector<CubicSegment> segments(Nint);
    for(size_t i=0;i<Nint;++i){
        segments[i].xc = xc[i];
        segments[i].x0 = x0[i];
        segments[i].x1 = x1[i];
        segments[i].a = sol(i*4+0);
        segments[i].b = sol(i*4+1);
        segments[i].c = sol(i*4+2);
        segments[i].d = sol(i*4+3);
    }

    PiecewiseCubicSpline *splineObj = new PiecewiseCubicSpline("");
    splineObj->SetSegments(segments);

    // Save coefficients
    std::ofstream out(Form("%s.txt", outFile));
    out << detID << " ";
    for(auto &s: segments){
        out << s.xc << " " << s.x0 << " " << s.x1 << " " << s.a << " " << s.b << " " << s.c << " " << s.d << std::endl;
    }
    out.close();
    std::cout<<"Saved coefficients to "<<outFile<<".txt\n";

    if (doPlot){
      // Reconstruct waveform
      int nGraphPts = 1000;
      TGraph* grRec = new TGraph(nGraphPts);
      double dx = (tMax-tMin)/(nGraphPts-1);
      for(int i=0;i<nGraphPts;++i){
          double x = tMin + i*dx;
          // find interval
          size_t k=0;
          for(;k<Nint;++k) if(x>=segments[k].x0 && x<=segments[k].x1) break;
          if(k==Nint) k=Nint-1;
          double y = splineObj->Eval(x);
          grRec->SetPoint(i,x,y);
      }

      // Draw
      TCanvas* c = new TCanvas("c","Global Weighted Cubic Fit",900,600);
      gr->SetMarkerStyle(20);
      gr->SetMarkerColor(kBlack);
      gr->Draw("AP");
      gr->SetTitle("Spline on automation points");
      grRec->SetLineColor(kBlue);
      grRec->SetLineWidth(2);
      grRec->Draw("L SAME");
      grRec->SetTitle("Reconstructed from C1 piece-wise cubic fit");
      TGraph* grSamples = new TGraph(Nint);
      for(size_t i=0;i<Nint;++i){
          double y = gr->Eval(xc[i]);
          grSamples->SetPoint(i, xc[i], y);
      }
      grSamples->SetMarkerStyle(21);
      grSamples->SetMarkerSize(1.2);
      grSamples->SetMarkerColor(kMagenta);
      grSamples->SetTitle("Automation ADC points");
      grSamples->Draw("P SAME");

      c->BuildLegend();
      c->SaveAs(Form("%s.root", outFile));
      c->SaveAs(Form("%s.png", outFile));

      std::cout<<"Black=Spline on automation points, Blue=reconstructed from cubic fit, Magenta=Automation ADC points\n";
    }
}


void resample_prof(
    TProfile *p,
    int detID,
    double dt=6.25,
    const char* outFile="coeffs",
    bool doPlot=false
){

  double max = p->GetMaximum();
  p->Scale(1.0 / max);

  resample(ProfileToGraph(p), detID, dt, outFile, doPlot);
}

