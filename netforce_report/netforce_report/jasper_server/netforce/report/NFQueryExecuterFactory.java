package netforce.report;

import java.util.Map;

import net.sf.jasperreports.engine.JRDataset;
import net.sf.jasperreports.engine.JRException;
import net.sf.jasperreports.engine.query.JRQueryExecuter;
import net.sf.jasperreports.engine.query.JRQueryExecuterFactory;
import net.sf.jasperreports.engine.util.JRProperties;

public class NFQueryExecuterFactory implements JRQueryExecuterFactory
{
    private final static Object[] NF_BUILTIN_PARAMETERS = {"NF_DATA","java.lang.string"};

    public Object[] getBuiltinParameters()
    {
        return NF_BUILTIN_PARAMETERS;
    }
	
	public JRQueryExecuter createQueryExecuter(JRDataset dataset, Map parameters)
			throws JRException
	{
		return new NFQueryExecuter(dataset, parameters);
	}

	public boolean supportsQueryParameterType(String className)
	{
		return true;
	}
}
