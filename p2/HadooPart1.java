import java.io.IOException;
import java.util.ArrayList;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.databind.node.ArrayNode;

public class HadooPart1{
	
	public static class ImageMapper extends Mapper<Object, Text, Text, Text>{

			private Text mDataK = new Text();
			private Text mDataV = new Text();
			private Text expQK = new Text();
			private Text expQV = new Text();

			public void map(Object key, Text value, Context con) 
			     throws IOException, InterruptedException {
				
				JsonNode jsonNode;
				JsonNode jArray;
				ObjectMapper objectMapper = new ObjectMapper();
				boolean comp = false;

				if(!value.toString().equals("")){

					jsonNode = objectMapper.readTree(value.toString());
					jArray = jsonNode.get("BIN_FCSKU_DATA");

					for(JsonNode jaux : jArray){ 
						com = parserData(jaux);
						if(com){
							mDataV.set(jaux.toString());			
							mDataK.set(jaux.get("typeName").asText());
							context.write(mDataK, mDataVm);		
							com = false;
						}
					}	
					expQV.set(jsonNode.get("EXPECTED_QUANTITY").asText());
					expQK.set("EXPECTED_QUANTITY");
					con.write(expQ, expQr);			
				}
			} 
		}


}