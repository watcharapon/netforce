package netforce.report;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Date;
import java.util.Iterator;
import java.util.List;
import java.util.StringTokenizer;

import net.sf.jasperreports.engine.data.JRAbstractTextDataSource;
import net.sf.jasperreports.engine.JRException;
import net.sf.jasperreports.engine.JRField;
import net.sf.jasperreports.engine.JRRewindableDataSource;
import net.sf.jasperreports.engine.util.JsonUtil;
import net.sf.jasperreports.repo.RepositoryUtil;

import org.json.simple.JSONValue;
import java.util.Map;
import java.util.HashMap;
import java.util.List;

import org.apache.commons.lang.StringUtils;

public class NFDataSource extends JRAbstractTextDataSource implements JRRewindableDataSource {

    Object data_obj;
    Object query_obj;
    Map context_map;
    List list_objs;
    int obj_ind;
    Object current_obj;

	public NFDataSource(String data, String query) throws JRException {
        System.out.println("NFDataSource data="+data+" query="+query);
        try {
            data_obj=JSONValue.parse(data);
        } catch (Exception e) {
            throw new JRException("Invalid JSON data");
        }
        query_obj=getDataPath(data_obj,query);
        context_map=getContextPath(data_obj,query);
        if (query_obj instanceof List) {
            list_objs=(List)query_obj;
            System.out.println("Query obj is List: "+list_objs.size());
        } else {
            list_objs=new ArrayList();
            list_objs.add(query_obj);
            System.out.println("Query obj is Map");
        }
        obj_ind=0;
        setDatePattern("yyyy-MM-dd");
	}
	
	public void moveFirst() throws JRException {
        System.out.println("moveFirst");
        current_obj=0;
	}

	public boolean next() {
        System.out.println("next");
        if (obj_ind>=list_objs.size()) {
            System.out.println("THE END "+obj_ind+" "+list_objs.size());
            return false;
        }
        Object val=list_objs.get(obj_ind++);
        if (val instanceof Map) {
            current_obj=new HashMap(context_map);
            ((Map)current_obj).putAll((Map)val);
        } else {
            current_obj=val; // XXX
        }
        System.out.println("still got some");
        return true;
	}

	public Object getFieldValue(JRField jrField) throws JRException 
	{
        String path=jrField.getName();
        System.out.println("getFieldValue "+path);
        Object val=getDataPath(current_obj,path);
        System.out.println("val: '"+val+"'");
        return val;
	}

    public Object getDataPath(Object data,String path) throws JRException {
        System.out.println("getDataPath "+path);
        String[] fields=StringUtils.split(path,'.');
        System.out.println("xXX "+fields.length);
        Object val=data;
        for (String field:fields) {
            if (val==null) break;
            System.out.println("  "+field);
            if (field.matches("^\\d+$")) {
                System.out.println("    list");
                int ind=Integer.parseInt(field);
                val=((List)val).get(ind); 
            } else {
                System.out.println("    map");
                val=((Map)val).get(field);
            }
        }
        return val;
    }

    public Map getContextPath(Object data,String path) throws JRException {
        System.out.println("getContextPath "+path);
        String[] fields=StringUtils.split(path,'.');
        Map context=new HashMap();
        Object val=data;
        for (String field:fields) {
            if (val==null) break;
            if (field.matches("^\\d+$")) {
                int ind=Integer.parseInt(field);
                val=((List)val).get(ind); 
            } else {
                context.putAll((Map)val);
                val=((Map)val).get(field);
            }
        }
        return context;
    }
}
