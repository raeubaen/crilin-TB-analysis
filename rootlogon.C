//modified 12/10/20222
// This is the file rootlogon.C
{
   TStyle *myStyle  = new TStyle("MyStyle","My Root Styles");

   myStyle->SetLegendBorderSize(0);
   // from ROOT plain style
   myStyle->SetCanvasBorderMode(0);
   myStyle->SetPadBorderMode(0);
   myStyle->SetPadColor(0);
   myStyle->SetCanvasColor(0);
   myStyle->SetTitleColor(1);
   myStyle->SetStatColor(0);

   myStyle->SetLabelSize(0.03,"xyz"); // size of axis values

   myStyle->SetHistLineWidth(2);
   myStyle->SetHistLineColor(kBlue+1);

   myStyle->SetLineWidth(2);
   myStyle->SetMarkerStyle(21);
   myStyle->SetMarkerColor(kBlue+1);

   //myStyle->SetLineStyleString(2,"[12 12]"); // postscript dashes
   //myStyle->SetErrorX(0.001);

   //myStyle->SetPadTickX(0);
   //myStyle->SetPadTickY(0);

   myStyle->SetLegendTextSize(0.04);

   myStyle->SetFuncColor(kRed+1);
   myStyle->SetFuncWidth(3);
   //myStyle->SetLineColor(kRed+1);

   myStyle->SetTitleFont(62, "X");
   myStyle->SetTitleFont(62, "Y");

   myStyle->SetLabelSize(0.05, "X");
   myStyle->SetTitleSize(0.05, "X");

   myStyle->SetLabelSize(0.05, "Y");
   myStyle->SetTitleSize(0.05, "Y");

   myStyle->SetTitleOffset(1.2, "Y");
   myStyle->SetTitleOffset(1.0, "X");

   // default canvas positioning
   //myStyle->SetCanvasDefX(900);
   //myStyle->SetCanvasDefY(20);
   //myStyle->SetCanvasDefH(550);
   //myStyle->SetCanvasDefW(540);

   myStyle->SetPadBottomMargin(0.15);
   //myStyle->SetPadTopMargin(0.3);
   myStyle->SetPadLeftMargin(0.15);
   //myStyle->SetPadRightMargin(0.1);
   //myStyle->SetPadTickX(0);
   //myStyle->SetPadTickY(0);
   //myStyle->SetFrameBorderMode(0);

   myStyle->SetTitleBorderSize(0);
   myStyle->SetOptTitle(0);

   // Din letter
   //myStyle->SetPaperSize(21, 28);

   myStyle->SetStatBorderSize(0);
   myStyle->SetStatX(0.85);
   myStyle->SetStatY(0.85);
   myStyle->SetStatFont(42);
   myStyle->SetOptStat(0);// Show overflow and underflow as well
   myStyle->SetOptFit(0);
   myStyle->SetPalette(1);

   // apply the new style
   gROOT->SetStyle("MyStyle"); //uncomment to set this style
   gROOT->ForceStyle(); // use this style, not the one saved in root files

   printf("\n Beginning new ROOT session with private TStyle \n");

}
