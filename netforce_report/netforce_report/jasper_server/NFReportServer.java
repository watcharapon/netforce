import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.ServletException;
 
import java.io.IOException;
import java.io.ByteArrayOutputStream;
 
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.server.Request;
import org.eclipse.jetty.server.handler.AbstractHandler;
import org.json.simple.JSONValue;

import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;

import net.sf.jasperreports.engine.JasperCompileManager;
import net.sf.jasperreports.engine.JasperExportManager;
import net.sf.jasperreports.engine.JasperFillManager;
import net.sf.jasperreports.engine.JasperPrint;
import net.sf.jasperreports.engine.JRPrintPage;
import net.sf.jasperreports.engine.JasperReport;
import net.sf.jasperreports.engine.design.JasperDesign;
import net.sf.jasperreports.engine.xml.JRXmlLoader;  
import net.sf.jasperreports.engine.query.JRQueryExecuterFactory;  
import net.sf.jasperreports.engine.util.JRProperties;  
import net.sf.jasperreports.engine.export.JRXlsExporter;
import net.sf.jasperreports.engine.export.JRXlsExporterParameter;

import java.io.FileInputStream;
import java.io.InputStream;
import java.io.File;
 
public class NFReportServer extends AbstractHandler
{
    public void handle(String target,
                       Request baseRequest,
                       HttpServletRequest request,
                       HttpServletResponse response) 
        throws IOException, ServletException
    {
        System.out.println("####################################################");
        System.out.println("RENDER JASPER REPORT");
        String report=request.getParameter("report");
        String data=request.getParameter("data");
        String format=request.getParameter("format");
        boolean multi_page=request.getParameter("multi_page")!=null;
        List<String> datas=new ArrayList();
        if (multi_page) {
            System.out.println("MULTI_PAGE");
            for (int i=0;; i++) {
                String d=request.getParameter("data_"+i);
                if (d==null) break;
                datas.add(d);
            }
            System.out.println("number of datas: "+datas.size());
        }

        File f=new File(report);
        String report_dir=f.getParent();

        byte[] report_data;
        try {
            InputStream input=new FileInputStream(report);
            System.out.println("Loading report...");
            JasperDesign design=JRXmlLoader.load(input);
            System.out.println("Compiling report...");
            JasperReport jreport=JasperCompileManager.compileReport(design);
            JasperPrint print;
            if (multi_page) {
                if (datas.size()==0) { // XXX
                    System.out.println("ERROR: no data in multi-page report!!!");
                }
                Map params=new HashMap();
                System.out.println("Filling report page "+1+"/"+datas.size()+"...");
                System.out.println("data: "+datas.get(0));
                params.put("NF_DATA",datas.get(0));
                params.put("SUBREPORT_DIR",report_dir);
                print=JasperFillManager.fillReport(jreport,params);
                for (int i=1; i<datas.size(); i++) {
                    Map params2=new HashMap();
                    System.out.println("Filling report page "+(i+1)+"/"+datas.size()+"...");
                    System.out.println("data: "+datas.get(i));
                    params2.put("NF_DATA",datas.get(i));
                    params2.put("SUBREPORT_DIR",report_dir);
                    JasperPrint print2=JasperFillManager.fillReport(jreport,params2);
                    List pages=print2.getPages();
                    for (int j=0; j<pages.size(); j++) {
                        JRPrintPage page=(JRPrintPage)pages.get(j);
                        print.addPage(page);
                    }
                }
            } else {
                Map params=new HashMap();
                params.put("NF_DATA",data);
                params.put("SUBREPORT_DIR",report_dir);
                System.out.println("Filling report...");
                print=JasperFillManager.fillReport(jreport,params);
            }
            if (format.equals("pdf")) {
                report_data=JasperExportManager.exportReportToPdf(print);
            } else if (format.equals("xls")) {
                ByteArrayOutputStream output=new ByteArrayOutputStream();
                JRXlsExporter exp=new JRXlsExporter();
                exp.setParameter(JRXlsExporterParameter.JASPER_PRINT,print); 
                exp.setParameter(JRXlsExporterParameter.OUTPUT_STREAM,output); 
                print.setProperty("net.sf.jasperreports.export.xls.white.page.background","false");
                exp.exportReport();
                report_data=output.toByteArray();
            } else {
                throw new ServletException("Invalid format: "+format);
            }
        } catch (Exception e) {
            e.printStackTrace();
            throw new ServletException("Failed to generate report: "+e.getMessage());
        }
    
        response.setStatus(HttpServletResponse.SC_OK);
        if (format.equals("pdf")) {
            response.setContentType("application/pdf");
            response.setHeader("Content-Disposition","attachment; filename=report.pdf");
        } else if (format.equals("xls")) {
            response.setContentType("application/vnd.ms-excel");
            response.setHeader("Content-Disposition","attachment; filename=report.xls");
        } else {
            throw new ServletException("Invalid format: "+format);
        }
        baseRequest.setHandled(true);
        response.getOutputStream().write(report_data);
    }
 
    public static void main(String[] args) throws Exception
    {
        Server server = new Server(9990);
        server.setHandler(new NFReportServer());
 
        server.start();
        server.join();
    }
}
