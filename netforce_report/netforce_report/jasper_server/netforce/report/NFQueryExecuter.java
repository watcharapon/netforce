package netforce.report;

import java.io.InputStream;
import java.util.Locale;
import java.util.Map;
import java.util.TimeZone;

import net.sf.jasperreports.engine.JRDataSource;
import net.sf.jasperreports.engine.JRDataset;
import net.sf.jasperreports.engine.JRException;
import net.sf.jasperreports.engine.data.JsonDataSource;
import net.sf.jasperreports.engine.query.JRAbstractQueryExecuter;

public class NFQueryExecuter extends JRAbstractQueryExecuter
{
	private NFDataSource datasource;
	
	public NFQueryExecuter(JRDataset dataset, Map parametersMap)
	{
		super(dataset, parametersMap);
		parseQuery();
	}

	protected String getParameterReplacement(String parameterName)
	{
		return String.valueOf(getParameterValue(parameterName));
	}

	public JRDataSource createDatasource() throws JRException
	{
		String data = (String) getParameterValue("NF_DATA");
		datasource = new NFDataSource(data, getQueryString());
		return datasource;
	}

	public void close()
	{
	}

	public boolean cancelQuery() throws JRException
	{
		return false;
	}
	
}
