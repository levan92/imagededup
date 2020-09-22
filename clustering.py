import math

def clustering(distance_map):
    '''
    Args
    ----
    distance_map:  Dict[filename:str,List[Tuple[filename:str, distance:int]]], generated from Hash.find_duplicates(scores=True)

    Returns
    -------
    List[ List[ filename:str ] ]
    '''
    clusters = []
    for filename, closest_matches in distance_map.items():
        if len(closest_matches) == 0:
            # no neighbours, start new cluster
            clusters.append([filename])
        else:
            # find cluster to join
            min_dist = math.inf
            min_cl_idx = None
            for cl_idx, cluster in enumerate(clusters):
                for candidate in cluster:

                    for tup in closest_matches:
                        if tup[0] == candidate and tup[1] < min_dist:
                            min_dist = tup[1]
                            min_cl_idx = cl_idx
                            break
                            
                    # in_match = [ tup for tup in closest_matches if tup[0]== candidate ]
                    # if len(in_match) > 0:
                    #     dist = in_match[0][1]
                    #     if dist < min_dist:
                    #         min_dist = dist
                    #         min_cl_idx = cl_idx

            if min_cl_idx is None:
                # start new cluster
                clusters.append([filename])
            else:
                # join closest cluster
                clusters[min_cl_idx].append(filename)
    return clusters
