import java.io.IOException;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
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


public class HadooPart1{
	
	public static class ImageMapper extends Mapper<Object, Text, Text, Text>{

		private Text binDataK = new Text();
		private Text binDataV = new Text();
		private Text expQK = new Text();
		private Text expQV = new Text();

		public void map(Object key, Text value, Context con) 
		     throws IOException, InterruptedException {
				
			JsonNode jsonNode;
			JsonNode jArray;
			ObjectMapper objectMapper = new ObjectMapper();

			if(!value.toString().equals("")){
				jsonNode = objectMapper.readTree(value.toString());
				jArray = jsonNode.get("BIN_FCSKU_DATA");
				for(JsonNode jvalue : jArray){ 
					if(!hasNull(jvalue)){
						
						binDataV.set(jvalue.toString());			
						binDataK.set(jvalue.get("asin").asText());
						con.write(binDataK, binDataV);		
					}	
				}

				expQV.set(jsonNode.get("EXPECTED_QUANTITY").asText());
				expQK.set("EXPECTED_QUANTITY");
				con.write(expQK, expQV);			
			}
		} 
	}

	public static class ImageReducer extends Reducer<Text,Text,Text,Text> {

		private Text expQvalue = new Text();
		
		public void reduce(Text key, Iterable<Text> values, Context con) 
		     throws IOException, InterruptedException {

			int q = 0;
			int items = 0;
			ObjectMapper objectMapper = new ObjectMapper();
			JsonNode jsonNode = null;
			JsonNode previous = null;
			boolean sameData = true;
			
			if(key.toString().equals("EXPECTED_QUANTITY")	){
				for (Text value : values) {
					jsonNode = objectMapper.readTree((value.toString()));
					q+=Integer.parseInt(value.toString());	
				}
				expQvalue.set(String.valueOf(q));
				con.write(key, expQvalue);
			}else{
				int i = 0;
				for(Text value: values){
					jsonNode = objectMapper.readTree((value.toString()));
					items+=Integer.parseInt(jsonNode.get("quantity").toString());	
					if (i==0){
						items++;
						previous = jsonNode;
						i++;
					}else{
						if(!sameMet(jsonNode,previous)){
							sameData = false;
						}
						
					}
					
				}
				
				((ObjectNode)jsonNode).put("items",items);
				((ObjectNode) jsonNode).put("identical",sameData);
				
				Text auxT = new Text();
				auxT.set(jsonNode.toString());
				con.write(key,auxT);	
			}
			
		}
	}
	
	public static boolean sameMet(JsonNode aux, JsonNode previous){
		boolean result = false;
		if(aux.get("name").toString().equals(previous.get("name").toString()) && aux.get("normalizedName").toString().equals(previous.get("normalizedName").toString())){
			if(aux.get("length").get("unit").toString().equals(previous.get("length").get("value").toString())){
				if(aux.get("weight").get("unit").toString().equals(previous.get("weight").get("value").toString())){
					if(aux.get("width").get("unit").toString().equals(previous.get("width").get("value").toString())){
						if(aux.get("height").get("unit").toString().equals(previous.get("height").get("value").toString())){
							result = true;
						}
					}	
				}
			}
		}
		
		return result;
	}

	public static boolean hasNull(JsonNode jsonNode){ 
		JsonNode aux;
		boolean hasNull=false;
		if((jsonNode.get("asin")!=null&&jsonNode.get("height")!=null&&jsonNode.get("length")!=null&&jsonNode.get("name")!=null
				&&jsonNode.get("normalizedName")!=null&&jsonNode.get("weight")!=null&&jsonNode.get("width")!=null)
				&&(jsonNode.get("asin").equals("null")==false&&jsonNode.get("height").equals("null")==false
				&&jsonNode.get("length").equals("null")==false&&jsonNode.get("name").equals("null")==false
				&&jsonNode.get("normalizedName").equals("null")==false&&jsonNode.get("weight").equals("null")==false
				&&jsonNode.get("width").equals("null")==false)){
			
			aux=jsonNode.get("height");
			if((aux.get("unit")==null||aux.get("value")==null)||(aux.get("unit").equals("null")==true||aux.get("value").equals("null")==true)){
				hasNull=true;
			}
			aux=jsonNode.get("length");
			if((aux.get("unit")==null||aux.get("value")==null)||(aux.get("unit").equals("null")==true||aux.get("value").equals("null")==true)){
				hasNull=true;
			}
			aux=jsonNode.get("weight");
			if((aux.get("unit")==null||aux.get("value")==null)||(aux.get("unit").equals("null")==true||aux.get("value").equals("null")==true)){
				hasNull=true;
			}
			aux=jsonNode.get("width");
			if((aux.get("unit")==null||aux.get("value")==null)||(aux.get("unit").equals("null")==true||aux.get("value").equals("null")==true)){
				hasNull=true;
			}
		}
		else
			hasNull=true;
		
		return hasNull;
	}
	
	public static class GetMapper extends Mapper<Object, Text, Text, Text>{

		private Text auxK = new Text();
		

		public void map(Object key, Text value, Context con)throws IOException, InterruptedException {
			
			auxK.set("Asins");
			con.write(auxK, value);
			
			} 
	}
		
	public static class GetReducer extends Reducer<Object, Text, Text, Text>{

		private int minName;
		private int maxName;
		private int minNN;
		private int maxNN;
		
		private String expQ;
		private float avWe,avWi,avH,avL;
		private String unitWe;
		private String unitWi;
		private String unitH;
		private String unitL;

		private int quantity = 0;
		
		int i = 0;
		int lName,lNameN = 0;
		float length, weight, width, height = 0;
		
		
		
		public void reduce(Object key, Iterable<Text> values, Context con) 
		     throws IOException, InterruptedException {
			ObjectMapper objectMapper = new ObjectMapper();
			JsonNode jsonNode ; 
			JsonNode jvalue;
			String[] aux;
			
			
			ObjectNode output = objectMapper.createObjectNode();
			ObjectNode medida = objectMapper.createObjectNode();
			ObjectNode result = objectMapper.createObjectNode();
			ObjectNode resultaux = objectMapper.createObjectNode();

			
			
			for(Text value:values){
				ObjectNode Node = objectMapper.createObjectNode();
				aux = value.toString().split("\t");
				if(aux[0].equals("EXPECTED_QUANTITY")){
					expQ = aux[1].toString();
				}else{
					jsonNode = objectMapper.readTree(aux[1].toString());
					
					jvalue = jsonNode.get("name");
					lName = jvalue.toString().length();
					jvalue = jsonNode.get("normalizedName");
					lNameN = jvalue.toString().length();
					jvalue = jsonNode.get("length");
					unitL = jvalue.get("unit").toString();
					length += Float.parseFloat(jvalue.get("value").toString());
					jvalue = jsonNode.get("weight");
					unitWe = jvalue.get("unit").toString();
					weight += Float.parseFloat(jvalue.get("value").toString());
					jvalue = jsonNode.get("width");
					unitWi = jvalue.get("unit").toString();
					width += Float.parseFloat(jvalue.get("value").toString());
					jvalue = jsonNode.get("height");
					unitH = jvalue.get("unit").toString();
					height += Float.parseFloat(jvalue.get("value").toString());
					
					quantity += Integer.parseInt(jsonNode.get("items").toString());
					
					
					if(i==0){
						minName = lName;
						maxName = lName;
						maxNN = lNameN;
						minNN = lNameN;
						i++;
					}else{
						if(lName<minName){
							minName = lName;
						}
						if(lName>maxName){
							maxName = lName;
						}
						if(lNameN<minNN){
							minNN = lNameN;
						}
						if(lNameN>maxNN){
							maxNN = lNameN;
						}
					}

					 Node.put("items",jsonNode.get("items").toString());
					 Node.put("identical",jsonNode.get("identical").toString());
					 resultaux.put(aux[0],Node);	
				}	
			}
			avH = height/quantity;
			avL = length/quantity;
			avWe = weight/quantity;
			avWi = width/quantity;
			output.put("EXPECTED_QUANTITY",expQ);
			
			medida.put("value",avH);
			medida.put("unit",unitH.toString());
			output.put("Averageheight", medida);
			medida = objectMapper.createObjectNode();
			
			medida.put("value",avL);
			medida.put("unit",unitL.toString());
			output.put("AverageLength", medida);
			medida = objectMapper.createObjectNode();
			
			medida.put("value",avWe);
			medida.put("unit",unitWe.toString());
			output.put("Averageweight", medida);
			medida = objectMapper.createObjectNode();
			
			medida.put("value",avWi);
			medida.put("unit",unitWi.toString());
			output.put("AverageWidth", medida);
			
			output.put("MinimunName",minName-2);
			output.put("MaximunName",maxName-2);
			
			output.put("MinimunNormalizedName",minNN-2);
			output.put("MaximunNormalizedName",maxNN-2);
			
			result.put("StatisticsBinImage", output);
			result.put("", resultaux);	
			Text resultado = new Text();
			resultado.set(result.toString());
			
			con.write(resultado, null);
			
		}
	}
		
	public static void main(String[] args) throws Exception {

		Configuration conf = new Configuration();
		String[] paths = new GenericOptionsParser(conf, args).getRemainingArgs();
		
		Job job = new Job(conf, "FirstMap");
		job.setJarByClass(HadooPart1.class);
		job.setMapperClass(ImageMapper.class);
		job.setReducerClass(ImageReducer.class);
		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(Text.class);
		FileInputFormat.addInputPath(job, new Path("data/mymetadata.json"));
		FileOutputFormat.setOutputPath(job, new Path(paths[0]));
		job.waitForCompletion(true);

		job = new Job(conf, "SecondMap");
		job.setJarByClass(HadooPart1.class);
		job.setMapperClass(GetMapper.class);
		job.setReducerClass(GetReducer.class);
		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(Text.class);

		FileInputFormat.addInputPath(job, new Path("salida/part-r-00000"));
		FileOutputFormat.setOutputPath(job, new Path("usr/"));
		System.exit(job.waitForCompletion(true) ? 0 : 1);
		

	}			
}
