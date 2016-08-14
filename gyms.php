<?php

ini_set('memory_limit', '256M');
ini_set('max_execution_time', 30);

	$gyms_array_to_encode = array();
	$json_encode_output = '';

	$db = new PDO( "sqlite:pogom.db" );

	if( isset( $_GET['after'] ) && !empty( $_GET['after'] ) ){
		$after_timestamp = (int) $_GET['after'] + 1;
		$datetime = new DateTime();
		$datetime->setTimestamp($after_timestamp);
		$after_date = $datetime->format('Y-m-d H:i:s.u');
		// var_dump( $after_date );
		$get_all_gyms = $db->prepare( "SELECT * FROM gym WHERE `last_modified` > '".$after_date."'" );
	}
	else {
		$get_all_gyms = $db->prepare( "SELECT * FROM gym" );
	}

	$last_modified = $db->prepare( "SELECT MAX(last_modified) FROM gym" );

	if( ! $get_all_gyms ){
		// var_dump( $get_all_gyms->errorInfo() );
	}

	if( ! $last_modified ){
		// var_dump( $last_modified->errorInfo() );
	}

	$all_gyms_query = $get_all_gyms->execute();
	$last_modified_query = $last_modified->execute();

	if( $all_gyms_query && $last_modified_query ){
	
		$last_modified_date = $last_modified->fetchColumn();
		$all_gyms_array = $get_all_gyms->fetchAll(PDO::FETCH_ASSOC);

		if( count( $all_gyms_array ) > 0 ){

			$date = new DateTime( $last_modified_date );
			$timestamp = $date->format('U');
			$gyms_array_to_encode['timestamp'] = $timestamp;

			foreach( $all_gyms_array as $gym ){

				$timestamp = '';
				$date = '';
				$last_modified = '';
				$tempdb = '';
				$gym_name = '';
				$result = '';
				$date = new DateTime( $gym['last_modified'] );
				$timestamp = $date->format('U');
				//$timestamp = $timestamp + 7200;
				$tempdb = new SQLite3('pogom.db');
				$result = $tempdb->query('SELECT gym_name FROM gymnames WHERE gym_id = "'.$gym['gym_id'].'"');
				$gym_name = $result->fetchArray();
				$gym_name = str_replace('\r', '', $gym_name[0]);

				$last_modified = substr( $gym['last_modified'], 0, 11 ) . (((int) substr( $gym['last_modified'], 11, 2 )) + 2 ) . substr( $gym['last_modified'], 13 );

				$gyms_array_to_encode['gyms'][] = array(
					$gym['gym_id'],
					$gym['latitude'],
					$gym['longitude'],
					$gym['team_id'],
					$gym['gym_points'],
					$last_modified,
					$gym_name,
					$timestamp
				);

			}

			$json_encode_output = json_encode( $gyms_array_to_encode );

		}
		/* No rows matched -- do something else */
		else {
			// echo "No rows matched the query.";
		}
	}

	echo $json_encode_output;

?>