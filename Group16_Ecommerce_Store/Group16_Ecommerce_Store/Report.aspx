<%@ Page Language="C#" AutoEventWireup="true" CodeBehind="Report.aspx.cs" Inherits="Group16_Ecommerce_Store.WebForm1" %>

<!DOCTYPE html>
<%--This page is for the reports that should be generated --%>
<html xmlns="http://www.w3.org/1999/xhtml">
<head runat="server">
    <title></title>
</head>
<body>
    <form id="form1" runat="server">
        <div class="container">
 
            <%-- Webpage Heading --%>
            <div class="row">
                <div class="col-xs-12">
                    <h1>Nebula Narratives</h1>
                </div>
            </div>
 
            <%-- Menu / Message --%>
            <div class="navbar-collapse collapse">
                <div class="col-sm-4">
                    <ul class="nav navbar-nav" style="font-weight: bold;">
                        <li>
                            <asp:HyperLink ID="hlHome" NavigateUrl="~/Default.aspx" runat="server">Home</asp:HyperLink><br />
                        </li>
                        <li>
                            <asp:HyperLink ID="hlCompanies" NavigateUrl="~/LoginForm.aspx" runat="server">s</asp:HyperLink><br />
                        </li>
                        <li>
                            <asp:HyperLink ID="hlEmployees" NavigateUrl="~/Report.aspx" runat="server">Reports</asp:HyperLink><br />
                        </li>
                    </ul>
                </div>
                <div class="col-sm-4">
                    <asp:Label ID="lblMessage" runat="server" Text="" />
                </div>
                <div class="col-sm-4" style="text-align: right;"></div>
            </div>
        </div>

    </form>
</body>
</html>
