#include "nndiff.h"
#include <cmath>

real nnval(real x_00, std::vector<real> const& params)
{
    real w_00__10 = params[0];
    real w_01__10 = params[1];
    real theta_10 = params[2];
    real w_00__11 = params[3];
    real w_01__11 = params[4];
    real theta_11 = params[5];
    real w_00__12 = params[6];
    real w_01__12 = params[7];
    real theta_12 = params[8];
    real w_00__13 = params[9];
    real w_01__13 = params[10];
    real theta_13 = params[11];
    real w_00__14 = params[12];
    real w_01__14 = params[13];
    real theta_14 = params[14];
    real w_10__20 = params[15];
    real w_11__20 = params[16];
    real w_12__20 = params[17];
    real w_13__20 = params[18];
    real w_14__20 = params[19];
    real theta_20 = params[20];
    real w_10__21 = params[21];
    real w_11__21 = params[22];
    real w_12__21 = params[23];
    real w_13__21 = params[24];
    real w_14__21 = params[25];
    real theta_21 = params[26];
    real w_10__22 = params[27];
    real w_11__22 = params[28];
    real w_12__22 = params[29];
    real w_13__22 = params[30];
    real w_14__22 = params[31];
    real theta_22 = params[32];
    real w_20__30 = params[33];
    real w_21__30 = params[34];
    real w_22__30 = params[35];
    real theta_30 = params[36];
    
    return -theta_30 + w_20__30/(exp(theta_20 - w_10__20/(exp(theta_10 - w_00__10*x_00 - w_01__10*log(x_00)) + 1) - w_11__20/(exp(theta_11 - w_00__11*x_00 - w_01__11*log(x_00)) + 1) - w_12__20/(exp(theta_12 - w_00__12*x_00 - w_01__12*log(x_00)) + 1) - w_13__20/(exp(theta_13 - w_00__13*x_00 - w_01__13*log(x_00)) + 1) - w_14__20/(exp(theta_14 - w_00__14*x_00 - w_01__14*log(x_00)) + 1)) + 1) + w_21__30/(exp(theta_21 - w_10__21/(exp(theta_10 - w_00__10*x_00 - w_01__10*log(x_00)) + 1) - w_11__21/(exp(theta_11 - w_00__11*x_00 - w_01__11*log(x_00)) + 1) - w_12__21/(exp(theta_12 - w_00__12*x_00 - w_01__12*log(x_00)) + 1) - w_13__21/(exp(theta_13 - w_00__13*x_00 - w_01__13*log(x_00)) + 1) - w_14__21/(exp(theta_14 - w_00__14*x_00 - w_01__14*log(x_00)) + 1)) + 1) + w_22__30/(exp(theta_22 - w_10__22/(exp(theta_10 - w_00__10*x_00 - w_01__10*log(x_00)) + 1) - w_11__22/(exp(theta_11 - w_00__11*x_00 - w_01__11*log(x_00)) + 1) - w_12__22/(exp(theta_12 - w_00__12*x_00 - w_01__12*log(x_00)) + 1) - w_13__22/(exp(theta_13 - w_00__13*x_00 - w_01__13*log(x_00)) + 1) - w_14__22/(exp(theta_14 - w_00__14*x_00 - w_01__14*log(x_00)) + 1)) + 1);

}

real NNPDFdev(real const& x_00, vector<real> const& params, 
	      real const& a, real const& b, real const& n)
{
    real w_00__10 = params[0];
    real w_01__10 = params[1];
    real theta_10 = params[2];
    real w_00__11 = params[3];
    real w_01__11 = params[4];
    real theta_11 = params[5];
    real w_00__12 = params[6];
    real w_01__12 = params[7];
    real theta_12 = params[8];
    real w_00__13 = params[9];
    real w_01__13 = params[10];
    real theta_13 = params[11];
    real w_00__14 = params[12];
    real w_01__14 = params[13];
    real theta_14 = params[14];
    real w_10__20 = params[15];
    real w_11__20 = params[16];
    real w_12__20 = params[17];
    real w_13__20 = params[18];
    real w_14__20 = params[19];
    real theta_20 = params[20];
    real w_10__21 = params[21];
    real w_11__21 = params[22];
    real w_12__21 = params[23];
    real w_13__21 = params[24];
    real w_14__21 = params[25];
    real theta_21 = params[26];
    real w_10__22 = params[27];
    real w_11__22 = params[28];
    real w_12__22 = params[29];
    real w_13__22 = params[30];
    real w_14__22 = params[31];
    real theta_22 = params[32];
    real w_20__30 = params[33];
    real w_21__30 = params[34];
    real w_22__30 = params[35];
    real theta_30 = params[36];
    return -n*b*pow(x_00, -a + 1)*pow(-x_00 + 1, b)*(-theta_30 + w_20__30/(exp(theta_20 - w_10__20/(exp(theta_10 - w_00__10*x_00 - w_01__10*log(x_00)) + 1) - w_11__20/(exp(theta_11 - w_00__11*x_00 - w_01__11*log(x_00)) + 1) - w_12__20/(exp(theta_12 - w_00__12*x_00 - w_01__12*log(x_00)) + 1) - w_13__20/(exp(theta_13 - w_00__13*x_00 - w_01__13*log(x_00)) + 1) - w_14__20/(exp(theta_14 - w_00__14*x_00 - w_01__14*log(x_00)) + 1)) + 1) + w_21__30/(exp(theta_21 - w_10__21/(exp(theta_10 - w_00__10*x_00 - w_01__10*log(x_00)) + 1) - w_11__21/(exp(theta_11 - w_00__11*x_00 - w_01__11*log(x_00)) + 1) - w_12__21/(exp(theta_12 - w_00__12*x_00 - w_01__12*log(x_00)) + 1) - w_13__21/(exp(theta_13 - w_00__13*x_00 - w_01__13*log(x_00)) + 1) - w_14__21/(exp(theta_14 - w_00__14*x_00 - w_01__14*log(x_00)) + 1)) + 1) + w_22__30/(exp(theta_22 - w_10__22/(exp(theta_10 - w_00__10*x_00 - w_01__10*log(x_00)) + 1) - w_11__22/(exp(theta_11 - w_00__11*x_00 - w_01__11*log(x_00)) + 1) - w_12__22/(exp(theta_12 - w_00__12*x_00 - w_01__12*log(x_00)) + 1) - w_13__22/(exp(theta_13 - w_00__13*x_00 - w_01__13*log(x_00)) + 1) - w_14__22/(exp(theta_14 - w_00__14*x_00 - w_01__14*log(x_00)) + 1)) + 1))/(-x_00 + 1) + n*pow(x_00, -a + 1)*pow(-x_00 + 1, b)*(-w_20__30*(w_10__20*(-w_00__10 - w_01__10/x_00)*exp(theta_10 - w_00__10*x_00 - w_01__10*log(x_00))/pow(exp(theta_10 - w_00__10*x_00 - w_01__10*log(x_00)) + 1, 2) + w_11__20*(-w_00__11 - w_01__11/x_00)*exp(theta_11 - w_00__11*x_00 - w_01__11*log(x_00))/pow(exp(theta_11 - w_00__11*x_00 - w_01__11*log(x_00)) + 1, 2) + w_12__20*(-w_00__12 - w_01__12/x_00)*exp(theta_12 - w_00__12*x_00 - w_01__12*log(x_00))/pow(exp(theta_12 - w_00__12*x_00 - w_01__12*log(x_00)) + 1, 2) + w_13__20*(-w_00__13 - w_01__13/x_00)*exp(theta_13 - w_00__13*x_00 - w_01__13*log(x_00))/pow(exp(theta_13 - w_00__13*x_00 - w_01__13*log(x_00)) + 1, 2) + w_14__20*(-w_00__14 - w_01__14/x_00)*exp(theta_14 - w_00__14*x_00 - w_01__14*log(x_00))/pow(exp(theta_14 - w_00__14*x_00 - w_01__14*log(x_00)) + 1, 2))*exp(theta_20 - w_10__20/(exp(theta_10 - w_00__10*x_00 - w_01__10*log(x_00)) + 1) - w_11__20/(exp(theta_11 - w_00__11*x_00 - w_01__11*log(x_00)) + 1) - w_12__20/(exp(theta_12 - w_00__12*x_00 - w_01__12*log(x_00)) + 1) - w_13__20/(exp(theta_13 - w_00__13*x_00 - w_01__13*log(x_00)) + 1) - w_14__20/(exp(theta_14 - w_00__14*x_00 - w_01__14*log(x_00)) + 1))/pow(exp(theta_20 - w_10__20/(exp(theta_10 - w_00__10*x_00 - w_01__10*log(x_00)) + 1) - w_11__20/(exp(theta_11 - w_00__11*x_00 - w_01__11*log(x_00)) + 1) - w_12__20/(exp(theta_12 - w_00__12*x_00 - w_01__12*log(x_00)) + 1) - w_13__20/(exp(theta_13 - w_00__13*x_00 - w_01__13*log(x_00)) + 1) - w_14__20/(exp(theta_14 - w_00__14*x_00 - w_01__14*log(x_00)) + 1)) + 1, 2) - w_21__30*(w_10__21*(-w_00__10 - w_01__10/x_00)*exp(theta_10 - w_00__10*x_00 - w_01__10*log(x_00))/pow(exp(theta_10 - w_00__10*x_00 - w_01__10*log(x_00)) + 1, 2) + w_11__21*(-w_00__11 - w_01__11/x_00)*exp(theta_11 - w_00__11*x_00 - w_01__11*log(x_00))/pow(exp(theta_11 - w_00__11*x_00 - w_01__11*log(x_00)) + 1, 2) + w_12__21*(-w_00__12 - w_01__12/x_00)*exp(theta_12 - w_00__12*x_00 - w_01__12*log(x_00))/pow(exp(theta_12 - w_00__12*x_00 - w_01__12*log(x_00)) + 1, 2) + w_13__21*(-w_00__13 - w_01__13/x_00)*exp(theta_13 - w_00__13*x_00 - w_01__13*log(x_00))/pow(exp(theta_13 - w_00__13*x_00 - w_01__13*log(x_00)) + 1, 2) + w_14__21*(-w_00__14 - w_01__14/x_00)*exp(theta_14 - w_00__14*x_00 - w_01__14*log(x_00))/pow(exp(theta_14 - w_00__14*x_00 - w_01__14*log(x_00)) + 1, 2))*exp(theta_21 - w_10__21/(exp(theta_10 - w_00__10*x_00 - w_01__10*log(x_00)) + 1) - w_11__21/(exp(theta_11 - w_00__11*x_00 - w_01__11*log(x_00)) + 1) - w_12__21/(exp(theta_12 - w_00__12*x_00 - w_01__12*log(x_00)) + 1) - w_13__21/(exp(theta_13 - w_00__13*x_00 - w_01__13*log(x_00)) + 1) - w_14__21/(exp(theta_14 - w_00__14*x_00 - w_01__14*log(x_00)) + 1))/pow(exp(theta_21 - w_10__21/(exp(theta_10 - w_00__10*x_00 - w_01__10*log(x_00)) + 1) - w_11__21/(exp(theta_11 - w_00__11*x_00 - w_01__11*log(x_00)) + 1) - w_12__21/(exp(theta_12 - w_00__12*x_00 - w_01__12*log(x_00)) + 1) - w_13__21/(exp(theta_13 - w_00__13*x_00 - w_01__13*log(x_00)) + 1) - w_14__21/(exp(theta_14 - w_00__14*x_00 - w_01__14*log(x_00)) + 1)) + 1, 2) - w_22__30*(w_10__22*(-w_00__10 - w_01__10/x_00)*exp(theta_10 - w_00__10*x_00 - w_01__10*log(x_00))/pow(exp(theta_10 - w_00__10*x_00 - w_01__10*log(x_00)) + 1, 2) + w_11__22*(-w_00__11 - w_01__11/x_00)*exp(theta_11 - w_00__11*x_00 - w_01__11*log(x_00))/pow(exp(theta_11 - w_00__11*x_00 - w_01__11*log(x_00)) + 1, 2) + w_12__22*(-w_00__12 - w_01__12/x_00)*exp(theta_12 - w_00__12*x_00 - w_01__12*log(x_00))/pow(exp(theta_12 - w_00__12*x_00 - w_01__12*log(x_00)) + 1, 2) + w_13__22*(-w_00__13 - w_01__13/x_00)*exp(theta_13 - w_00__13*x_00 - w_01__13*log(x_00))/pow(exp(theta_13 - w_00__13*x_00 - w_01__13*log(x_00)) + 1, 2) + w_14__22*(-w_00__14 - w_01__14/x_00)*exp(theta_14 - w_00__14*x_00 - w_01__14*log(x_00))/pow(exp(theta_14 - w_00__14*x_00 - w_01__14*log(x_00)) + 1, 2))*exp(theta_22 - w_10__22/(exp(theta_10 - w_00__10*x_00 - w_01__10*log(x_00)) + 1) - w_11__22/(exp(theta_11 - w_00__11*x_00 - w_01__11*log(x_00)) + 1) - w_12__22/(exp(theta_12 - w_00__12*x_00 - w_01__12*log(x_00)) + 1) - w_13__22/(exp(theta_13 - w_00__13*x_00 - w_01__13*log(x_00)) + 1) - w_14__22/(exp(theta_14 - w_00__14*x_00 - w_01__14*log(x_00)) + 1))/pow(exp(theta_22 - w_10__22/(exp(theta_10 - w_00__10*x_00 - w_01__10*log(x_00)) + 1) - w_11__22/(exp(theta_11 - w_00__11*x_00 - w_01__11*log(x_00)) + 1) - w_12__22/(exp(theta_12 - w_00__12*x_00 - w_01__12*log(x_00)) + 1) - w_13__22/(exp(theta_13 - w_00__13*x_00 - w_01__13*log(x_00)) + 1) - w_14__22/(exp(theta_14 - w_00__14*x_00 - w_01__14*log(x_00)) + 1)) + 1, 2)) + n*pow(x_00, -a + 1)*(-a + 1)*pow(-x_00 + 1, b)*(-theta_30 + w_20__30/(exp(theta_20 - w_10__20/(exp(theta_10 - w_00__10*x_00 - w_01__10*log(x_00)) + 1) - w_11__20/(exp(theta_11 - w_00__11*x_00 - w_01__11*log(x_00)) + 1) - w_12__20/(exp(theta_12 - w_00__12*x_00 - w_01__12*log(x_00)) + 1) - w_13__20/(exp(theta_13 - w_00__13*x_00 - w_01__13*log(x_00)) + 1) - w_14__20/(exp(theta_14 - w_00__14*x_00 - w_01__14*log(x_00)) + 1)) + 1) + w_21__30/(exp(theta_21 - w_10__21/(exp(theta_10 - w_00__10*x_00 - w_01__10*log(x_00)) + 1) - w_11__21/(exp(theta_11 - w_00__11*x_00 - w_01__11*log(x_00)) + 1) - w_12__21/(exp(theta_12 - w_00__12*x_00 - w_01__12*log(x_00)) + 1) - w_13__21/(exp(theta_13 - w_00__13*x_00 - w_01__13*log(x_00)) + 1) - w_14__21/(exp(theta_14 - w_00__14*x_00 - w_01__14*log(x_00)) + 1)) + 1) + w_22__30/(exp(theta_22 - w_10__22/(exp(theta_10 - w_00__10*x_00 - w_01__10*log(x_00)) + 1) - w_11__22/(exp(theta_11 - w_00__11*x_00 - w_01__11*log(x_00)) + 1) - w_12__22/(exp(theta_12 - w_00__12*x_00 - w_01__12*log(x_00)) + 1) - w_13__22/(exp(theta_13 - w_00__13*x_00 - w_01__13*log(x_00)) + 1) - w_14__22/(exp(theta_14 - w_00__14*x_00 - w_01__14*log(x_00)) + 1)) + 1))/x_00;
}
