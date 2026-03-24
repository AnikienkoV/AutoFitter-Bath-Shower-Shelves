import c4d
import math
import struct
from c4d import gui
from c4d import utils
from c4d.utils import SplineHelp, SplineLengthData
import ast
import traceback
from c4d import Vector
from itertools import chain


version = '260323'


test_mode = False


def debug(inf):
    if test_mode:
        print(f"[AutoFitter] {inf}")


def fix_matrix(i):
    global_pos = i.GetMg().off

    # remove Y to let hang or lift items
    global_pos = c4d.Vector(global_pos.x, 0, global_pos.z)
    return global_pos


def fix_matrix_nulls_only(i):
    parent = i.GetUp()
    full_parent_matrix = c4d.Matrix()

    while parent:
        full_parent_matrix *= parent.GetMg()
        parent = parent.GetUp()
    return full_parent_matrix


def parents_rotation(i):

    parent = i.GetUp()
    parent_rotation = c4d.utils.Rad(0)
    while parent:
        parent_rotation -= parent[c4d.ID_BASEOBJECT_REL_ROTATION, c4d.VECTOR_X]
        parent = parent.GetUp()

    return parent_rotation



def point_position(global_matrix, points, i):
    second_global_point = global_matrix * points[i]
    second_point_x = second_global_point.x
    second_point_z = second_global_point.z
    return second_point_x, second_point_z


# arguments - item, item type
def Get_Data_From_Spline_Points(furniture_item, furniture_selected, Rooms_Splines):

    try:
        if furniture_item == None:
            return
        furniture_item_name = furniture_item.GetName()
        furniture_item_name = furniture_item_name.lower()

        furniture_type = furniture_selected


        if Rooms_Splines != None:
            Rooms_Splines_name = Rooms_Splines.GetName()
            Rooms_Splines_name = Rooms_Splines_name.lower()
        else:
            Rooms_Splines_name = ''


        if 'splines' not in Rooms_Splines_name:
            Walls_Null = Rooms_Splines.GetUp()
            Walls_Null_children = Walls_Null.GetChildren()
            for Null in Walls_Null_children:

                if Null != None:
                    Null_name = Null.GetName()
                    Null_name = Null_name.lower()
                else:
                    Null_name = ''




        Rooms_Splines = Rooms_Splines.GetChildren()


        #for spline in Rooms_Splines:
        for spline in Rooms_Splines:


            # ignore primitive objects - circles, rectangle, ect
            if spline and spline.GetType() != c4d.Ospline:
                continue


            if spline[c4d.ID_BASEOBJECT_GENERATOR_FLAG] == False:
                continue

            if spline != None:
                spoted_spline_name = spline.GetName()
                spoted_spline_name = spoted_spline_name.lower()
            else:
                spoted_spline_name = ''

            sh = SplineHelp()
            sh.InitSpline(spline)

            #print (spline)

            points = spline.GetAllPoints()
            #global_matrix = spline.GetMg()


            #global_matrix = c4d.Matrix(fix_matrix(spline))
            global_matrix = c4d.Matrix(spline.GetMg())


            global_matrix = c4d.Matrix(fix_matrix(spline))
            global_matrix = c4d.Matrix(spline.GetMg())


            for index, point in enumerate(points):


                global_point = global_matrix * points[index]

                if global_point != None:

                    first_point_x = global_point.x
                    first_point_z = global_point.z


                    # Fake Snap Tool
                    Threshold = 3
                    approximate_first_point_pos_x_min = first_point_x - Threshold
                    approximate_first_point_pos_x_max = first_point_x + Threshold

                    approximate_first_point_pos_z_min = first_point_z - Threshold
                    approximate_first_point_pos_z_max = first_point_z + Threshold


                    item_pos = fix_matrix(furniture_item)

                    furniture_item_x = item_pos.x
                    furniture_item_z = item_pos.z


                    # Search points
                    Threshold = 1


                    approximate_first_point_pos_x_min = first_point_x - Threshold
                    approximate_first_point_pos_x_max = first_point_x + Threshold

                    approximate_first_point_pos_z_min = first_point_z - Threshold
                    approximate_first_point_pos_z_max = first_point_z + Threshold


                    # in range() not suitible here, because it uses only int numbers
                    if approximate_first_point_pos_x_min < furniture_item_x < approximate_first_point_pos_x_max:
                        if approximate_first_point_pos_z_min < furniture_item_z < approximate_first_point_pos_z_max:

                            first_point = index


                            all_points = len(points)

                            def looped_index(i):
                                return i % all_points

                            minus_three_point_x, minus_three_point_z = point_position(global_matrix, points,  looped_index(first_point + 4))
                            minus_two_point_x, minus_two_point_z = point_position(global_matrix, points, looped_index(first_point + 3))
                            minus_one_point_x, minus_one_point_z = point_position(global_matrix, points, looped_index(first_point + 2))
                            zero_point_x, zero_point_z = point_position(global_matrix, points, looped_index(first_point + 1))
                            # first
                            second_point_x, second_point_z = point_position(global_matrix, points, looped_index(first_point - 1))
                            third_point_x, third_point_z = point_position(global_matrix, points, looped_index(first_point - 2))
                            fourth_point_x, fourth_point_z = point_position(global_matrix, points, looped_index(first_point - 3))
                            fifth_point_x, fifth_point_z = point_position(global_matrix, points, looped_index(first_point - 4))


                            second_point_x = round(second_point_x, 3)
                            second_point_z = round(second_point_z, 3)
                            third_point_x  = round(third_point_x, 3)
                            third_point_z  = round(third_point_z, 3)
                            fourth_point_x = round(fourth_point_x, 3)
                            fourth_point_z = round(fourth_point_z, 3)
                            fifth_point_x  = round(fifth_point_x, 3)
                            fifth_point_z  = round(fifth_point_z, 3)


                            previouse_segment_length = ((first_point_x - zero_point_x) ** 2 + (first_point_z - zero_point_z) ** 2) ** 0.5

                            # for L and U shaped, calculate length of next wall
                            next_segment_length = ((third_point_x - second_point_x) ** 2 + (third_point_z - second_point_z) ** 2) ** 0.5
                            third_segment_length = ((fourth_point_x - third_point_x) ** 2 + (fourth_point_z - third_point_z) ** 2) ** 0.5


                            # Angle betwwen two points for rotation
                            def prepare_data_for_angles_calculations(fst_point_x, fst_point_z, sec_point_x, sec_point_z):
                                m_x = sec_point_x - fst_point_x
                                m_z = sec_point_z - fst_point_z

                                return m_x, m_z

                            mid_x, mid_z = prepare_data_for_angles_calculations(first_point_x, first_point_z, second_point_x, second_point_z)


                            # length
                            length = ((second_point_x - first_point_x) ** 2 + (second_point_z - first_point_z) ** 2) ** 0.5


                            depth = min(previouse_segment_length, next_segment_length)

                            depth = round(depth, 3)

                            #print(previouse_segment_length)
                            #print(next_segment_length)


                            if furniture_item[c4d.ID_BASEOBJECT_REL_SCALE,c4d.VECTOR_X] > 0:

                                mid_x, mid_z = prepare_data_for_angles_calculations(first_point_x, first_point_z, second_point_x, second_point_z)
                                angle_rad = math.atan2(mid_z, mid_x) + c4d.utils.Rad(360) + parents_rotation(furniture_item)

                            if furniture_item[c4d.ID_BASEOBJECT_REL_SCALE,c4d.VECTOR_X] < 0:

                                mid_x, mid_z = prepare_data_for_angles_calculations(zero_point_x, zero_point_z, first_point_x, first_point_z)
                                angle_rad = math.atan2(mid_z, mid_x) + c4d.utils.Rad(360) + parents_rotation(furniture_item)

                                length = ((second_point_x - third_point_x) ** 2 + (second_point_z - third_point_z) ** 2) ** 0.5


                            length = round(length, 3)


                            # angle normalization
                            if int(c4d.utils.Deg(angle_rad) ) == 360:
                                pass
                            else:
                                angle_rad = (angle_rad % c4d.utils.Rad(360) + c4d.utils.Rad(360)) % c4d.utils.Rad(360)

                            # Tub or Shower
                            if furniture_type == 2:
                                return length, depth, angle_rad

                            # Shelving
                            elif furniture_type == 8:
                                return length, angle_rad, next_segment_length, third_segment_length, spoted_spline_name



    except:
        print("An error occurred:")
        traceback.print_exc()



def shelves_fillin(item, length, length_depth, third_segment_length):
    debug('105 - Start shelves fillin')

    profile = item[800201]

    wire_shelves = False

    # check is it wire shelf (not solid)
    wire_type_of_shelve = profile.CheckType(c4d.Osplinecircle)


    default_offset_value = 14

    if wire_type_of_shelve:
        default_offset_value = 0

    # L shape
    if item[c4d.SHELVES_MODE] == 1:
        if wire_type_of_shelve:
            length_depth_correction = 12
        else:
            length_depth_correction = 14

        item[10004] = length_depth + length_depth_correction

        debug(f"106 - L shape shelve, length_depth: {length_depth}, length_depth_correction: {length_depth_correction}, final length_depth: {item[10004]}")

    # U shape
    elif item[c4d.SHELVES_MODE] == 2:
        item[10004] = round(length_depth)

        debug(f"107 - U shape shelve, length_depth: {length_depth}, final length_depth: {item[10004]}")

        length = round(length, 3)

        third_segment_length = round(third_segment_length, 3)

        debug(f"108 - U shape shelve, length: {length}, third_segment_length: {third_segment_length}")


        if length < third_segment_length:

            debug("109 - U shape shelve, length < third_segment_length")

            two_segments_difference = third_segment_length - length

            third_length_correction = default_offset_value - two_segments_difference - 0.5

            third_length_correction = int(third_length_correction)

            item[c4d.SIDE_3_OFFSET_END] = third_length_correction

            debug(f"110 - Final third_length_correction: {item[c4d.SIDE_3_OFFSET_END]}")

        elif length > third_segment_length:

            debug("111 - U shape shelve, length > third_segment_length")

            two_segments_difference = length - third_segment_length

            third_length_correction = default_offset_value + two_segments_difference

            third_length_correction = int(third_length_correction)

            item[c4d.SIDE_3_OFFSET_END] = third_length_correction

            debug(f"112 - Final third_length_correction: {item[c4d.SIDE_3_OFFSET_END]}")

        # equal sides case
        else:
            debug("113 - U shape shelve, length == third_segment_length")

            item[c4d.SIDE_3_OFFSET_END] = default_offset_value

            debug(f"114 - Final third_length_correction: {item[c4d.SIDE_3_OFFSET_END]}")

        c4d.EventAdd()

    else:
        debug("115 - Straight shelve, no length_depth correction needed")



# corners
def automation_by_hovering_on_corners(Rooms_Splines):
    doc = c4d.documents.GetActiveDocument()


    selected = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)


    for item in selected:
        # when only ONE item selected
        if len(selected) < 2:


            if item != None:
                selected_item_name = item.GetName()
                selected_item_name = selected_item_name.lower()
                #print(selected_item_name)
            else:
                selected_item_name = ''

            match = False

            # Bath
            #elif 'Tub' in selected_item_name:
            if 'tub/shower' in selected_item_name and 'combo tub/shower' not in selected_item_name:
                #print('Tub/Shower Selected')

                match = Get_Data_From_Spline_Points(item, 2, Rooms_Splines)

                # spline not sploted
                if match != None:


                    length, width, angle = Get_Data_From_Spline_Points(item, 2, Rooms_Splines)


                    if length and angle:


                        # length
                        # 150% it is max input, so it is a limit
                        item[c4d.ID_USERDATA,2] = length / 60


                        # place shorterst side wall size as width
                        if width < 50:

                            correction =  35 / 1120
                            final_width = correction * width

                            item[c4d.ID_USERDATA,1] = final_width


                        # for both long walls put default width
                        else:
                            item[c4d.ID_USERDATA,1] = 1


                        # rotation
                        item[c4d.ID_BASEOBJECT_REL_ROTATION,c4d.VECTOR_X] = angle - c4d.utils.Rad(270)

                        c4d.EventAdd()

                        return match



            # Combo Tub/Shower
            elif 'combo tub/shower' in selected_item_name:

                match = Get_Data_From_Spline_Points(item, 2, Rooms_Splines)

                # spline not sploted
                if match != None:
                    length, width, angle = Get_Data_From_Spline_Points(item, 2, Rooms_Splines)

                    if length and angle:


                        #length
                        # 150% it is max input, so it is a limit
                        item[10002] = length


                        # width

                        # place shorterst side wall size as width
                        if width < 50:
                            item[10003] = width
                        # for both long walls put default width
                        else:
                            pass


                        item[c4d.ID_BASEOBJECT_REL_ROTATION,c4d.VECTOR_X] = angle# - c4d.utils.Rad(270)

                        c4d.EventAdd()

                        return match






            # Shower has other input
            elif 'shower' in selected_item_name and 'combo tub/shower' not in selected_item_name and 'tub/shower' not in selected_item_name:

                match = Get_Data_From_Spline_Points(item, 2, Rooms_Splines)

                # spline not sploted
                if match != None:
                    length, width, angle = Get_Data_From_Spline_Points(item, 2, Rooms_Splines)

                    if length and angle:


                        # length
                        # 50 it is max input, so it is a limit
                        if length > 90:
                            item[c4d.ID_USERDATA,1] = 90
                        else:
                            item[c4d.ID_USERDATA,1] = length - 1


                        # width
                        if width < 50:
                            item[c4d.ID_USERDATA,2] = width - 0.5
                        else:
                            item[c4d.ID_USERDATA,2] = 40


                        item[c4d.ID_BASEOBJECT_REL_ROTATION,c4d.VECTOR_X] = angle

                        c4d.EventAdd()

                        return match





            # Shelves
            elif 'shelving' in selected_item_name:

                match = Get_Data_From_Spline_Points(item, 8, Rooms_Splines)

                if match != None:
                    length, angle, length_depth, third_segment_length, spline_name = Get_Data_From_Spline_Points(item, 8, Rooms_Splines)


                    if length and angle:
                        item[c4d.ID_BASEOBJECT_REL_ROTATION,c4d.VECTOR_X] = angle


                        item[10003] = length

                        shelves_fillin(item, length, length_depth, third_segment_length)

                        c4d.EventAdd()

                        return match






# collect items data to pass throug function
def get_selected_item_data(item):

    # item name
    selected_item_name = item.GetName()
    selected_item_name = selected_item_name.lower()


    # parent name
    parent = item.GetUp()
    if parent:
        parent_name = item.GetName()
        parent_name = parent_name.lower()

        parent_rotation = parent[c4d.ID_BASEOBJECT_REL_ROTATION,c4d.VECTOR_X]

    else:
        parent_name = ''
        parent_rotation = c4d.utils.Rad(0)


    # item pos
    item_mg = item.GetMg()
    item_pos = item_mg.off
    item_pos = c4d.Vector(item_pos.x, 0, item_pos.z)

    # item true rotation
    item_rotation = item[c4d.ID_BASEOBJECT_REL_ROTATION,c4d.VECTOR_X]
    item_true_angle = item_rotation + parent_rotation



    # check item mirroring
    if item[c4d.ID_BASEOBJECT_REL_SCALE,c4d.VECTOR_X] < 0:
        mirroring_by_scale = True
    else:
        mirroring_by_scale = False

    return selected_item_name, item_pos, item_true_angle, mirroring_by_scale, parent_name



# extend_to_the_end_of_wall or virtual wall point
def length_to_the_point(pass_through_item, pass_through_item_name, pass_through_pos, pass_through_rotation, mirroring_by_scale, put_detection_distance, put_angle_correction, Rooms_Splines):
    debug('004 - Start length to the point')

    debug(f"005 - pass_through_item_name: {pass_through_item_name}, pass_through_pos: {pass_through_pos}, pass_through_rotation: {c4d.utils.Deg(pass_through_rotation)}, mirroring_by_scale: {mirroring_by_scale}, put_detection_distance: {put_detection_distance}, put_angle_correction: {c4d.utils.Deg(put_angle_correction)}")
    doc = c4d.documents.GetActiveDocument()

    wall_splines = Rooms_Splines
    if wall_splines == None:
        debug("006 - No wall splines found")
        return

    wall_splines_null = wall_splines

    if wall_splines != None:
        debug("007 - Wall splines found")
        wall_splines_name = wall_splines.GetName()
        wall_splines_name = wall_splines_name.lower()
    else:
        wall_splines_name = ''

    wall_splines = wall_splines.GetChildren()

    #print('wall_splines', wall_splines)


    start_pos = pass_through_pos

    all_neares_distances = []





    # omagenery line to spot wall corner (spline point)
    def is_point_on_line(point):
        debug('008 - Start is_point_on_line function')

        item = pass_through_item
        parent = item.GetUp()
        selected_item_name = pass_through_item_name


        # 120 because cabinet with pivot on right need to be spoted even if it is long
        if 'shelving' in selected_item_name:
            imaginary_line_length = 300
        else:
            imaginary_line_length = 81
        threshold = 1


        #angle_rad = math.radians(0)
        angle_rad = item[c4d.ID_BASEOBJECT_REL_ROTATION,c4d.VECTOR_X] + c4d.utils.Rad(180) - parents_rotation(item)
        if 'shelving' in selected_item_name:
            angle_rad = item[c4d.ID_BASEOBJECT_REL_ROTATION,c4d.VECTOR_X] - parents_rotation(item)
        elif 'tub/shower' in selected_item_name and 'combo tub/shower' not in selected_item_name:
            angle_rad = item[c4d.ID_BASEOBJECT_REL_ROTATION,c4d.VECTOR_X] - parents_rotation(item) - c4d.utils.Rad(90)
        elif 'combo tub/shower' in selected_item_name:
            angle_rad = item[c4d.ID_BASEOBJECT_REL_ROTATION,c4d.VECTOR_X] - parents_rotation(item)
        elif 'shower' in selected_item_name and 'combo tub/shower' not in selected_item_name and 'tub/shower' not in selected_item_name:
            angle_rad = item[c4d.ID_BASEOBJECT_REL_ROTATION,c4d.VECTOR_X] - parents_rotation(item)



        # start = item.GetMg().off
        # start = c4d.Vector(start.x, 0, start.z)

        start = pass_through_pos

        end = start_pos + c4d.Vector(math.cos(angle_rad) * imaginary_line_length, 0, math.sin(angle_rad) * imaginary_line_length)


        #end pos test
        if test_mode:
            Cube_tester = doc.SearchObject('Cube_tester')
            if Cube_tester != None:
                Cube_tester[c4d.ID_BASEOBJECT_REL_POSITION] = end



        line_vec = c4d.Vector(end.x - start.x, 0, end.z - start.z)
        point_vec = c4d.Vector(point.x - start.x, 0, point.z - start.z)






        line_length = line_vec.GetLength()
        if line_length == 0:
            return False, None

        projection_factor = point_vec.Dot(line_vec) / (line_length ** 2)


        if not (-0.01 <= projection_factor <= 1.01):

            return False, None

        # Clamp projection_factor inside [0, 1]
        projection_factor = max(0.0, min(1.0, projection_factor))

        projection = projection_factor * line_vec
        nearest_point = start + projection

        distance = (point - nearest_point).GetLength()
        distance = round(distance, 3)

        calculated_distance = projection_factor * line_length
        calculated_distance = round(calculated_distance, 3)


        #print(f"Point: {point}, projection_factor: {projection_factor}, distance: {distance}, threshold: {threshold}")

        if distance <= threshold:
            debug(f"009 - Point is on line, distance: {distance}, calculated_distance: {calculated_distance}")

            return True, calculated_distance

        else:
            debug(f"009 - Point is NOT on line, distance: {distance}, threshold: {threshold}")

            return False, None





    #start_pos = item.GetMg().off
    item_x_poz = start_pos.x
    item_z_poz = start_pos.z


    all_positions_on_line = []
    point_on_line = []


    if 'splines' not in wall_splines_name:
        Walls_Null = wall_splines_null.GetUp()
        Walls_Null_children = Walls_Null.GetChildren()
        for Null in Walls_Null_children:

            if Null != None:
                Null_name = Null.GetName()
                Null_name = Null_name.lower()
            else:
                Null_name = ''



    for spline in wall_splines:
        debug(f"014 - Checking spline: {spline.GetName()}")


        if spline and spline.GetType() != c4d.Ospline:
            continue

        if spline[c4d.ID_BASEOBJECT_GENERATOR_FLAG] == False:
            continue


        sh = SplineHelp()
        sh.InitSpline(spline)

        points = spline.GetAllPoints()


        global_matrix = c4d.Matrix(fix_matrix(spline))
        global_matrix = c4d.Matrix(spline.GetMg())


        # wall corner spoting
        for index, point in enumerate(points):

            debug(f"015 - Checking point {index} of spline {spline.GetName()}: {point}")

            global_point = global_matrix * points[index]
            s_point_x = global_point.x
            s_point_z = global_point.z

            spline_point_pos = c4d.Vector(s_point_x, 0, s_point_z)


            is_on_line, _ = is_point_on_line(spline_point_pos)


            if is_on_line:


                all_positions_on_line.append(spline_point_pos)
                point_on_line.append(point)

                debug(f"016 - all_positions_on_line: {all_positions_on_line}, point_on_line: {point_on_line}")




    # spotting wall by virtual points
    # positive infinity
    shortest_distance = float('inf')
    closest_point = None

    for i, pos in enumerate(all_positions_on_line):
        dist = (pos - start_pos).GetLength()
        if dist < shortest_distance:
            shortest_distance = dist
            closest_point = point_on_line[i]
            near_corner_pos = pos

            debug(f"017 - New closest point found: {closest_point}, distance: {shortest_distance}")



    # Use the closest_cabinet if found
    if closest_point is not None:

        debug(f"018 - Closest point to the line: {closest_point}, near_corner_pos: {near_corner_pos}, shortest_distance: {shortest_distance}")


        near_corner_x_pos = near_corner_pos.x
        near_corner_z_pos = near_corner_pos.z

        near_corner_x_pos = round(near_corner_x_pos, 3)
        near_corner_z_pos = round(near_corner_z_pos, 3)



        length_to_near_corner = ((near_corner_x_pos - item_x_poz) ** 2 + (near_corner_z_pos - item_z_poz) ** 2) ** 0.5
        length_to_near_corner = round(length_to_near_corner, 3)

        if mirroring_by_scale: #item[c4d.ID_BASEOBJECT_REL_SCALE,c4d.VECTOR_X] < 0:
            pass


        final_length = length_to_near_corner


        if final_length > 1:

            # prevent usage cabinet after wall corner, by taking shorter distance


            for spline in wall_splines:

                debug(f"019 - Final check on spline: {spline.GetName()} for point: {closest_point}")


                # ignore primitive objects - circles, rectangle, ect
                if spline and spline.GetType() != c4d.Ospline:
                    continue

                if spline[c4d.ID_BASEOBJECT_GENERATOR_FLAG] == False:
                    continue

                if spline != None:
                    spoted_spline_name = spline.GetName()
                    spoted_spline_name = spoted_spline_name.lower()
                else:
                    spoted_spline_name = ''

                sh = SplineHelp()
                sh.InitSpline(spline)

                #print (spline)

                points = spline.GetAllPoints()

                global_matrix = c4d.Matrix(spline.GetMg())


                global_matrix = c4d.Matrix(fix_matrix(spline))
                global_matrix = c4d.Matrix(spline.GetMg())



                for index, point in enumerate(points):

                    debug(f"020 - Checking point {index} of spline {spline.GetName()} for final length calculation: {point}")


                    global_point = global_matrix * points[index]

                    if global_point != None:

                        first_point_x = global_point.x
                        first_point_z = global_point.z



                        if global_point == near_corner_pos:

                            debug(f"021 - Near corner position {near_corner_pos} found at point {index} of spline {spline.GetName()}")

                            # points = spline.GetAllPoints()

                            spline_name = spline.GetName()

                            all_points = len(points)


                            def looped_index(i):
                                return i % all_points


                            first_point = looped_index(index + 1)


                            global_point = global_matrix * points[first_point]

                            minus_three_point_x, minus_three_point_z = point_position(global_matrix, points, looped_index(first_point + 4))
                            minus_two_point_x, minus_two_point_z = point_position(global_matrix, points, looped_index(first_point + 3))
                            minus_one_point_x, minus_one_point_z = point_position(global_matrix, points, looped_index(first_point + 2))
                            zero_point_x, zero_point_z = point_position(global_matrix, points, looped_index(first_point + 1))
                            # first
                            first_point_x, first_point_z = point_position(global_matrix, points, first_point)
                            second_point_x, second_point_z = point_position(global_matrix, points, looped_index(first_point - 1))
                            third_point_x, third_point_z = point_position(global_matrix, points, looped_index(first_point - 2))
                            fourth_point_x, fourth_point_z = point_position(global_matrix, points, looped_index(first_point - 3))
                            fifth_point_x, fifth_point_z = point_position(global_matrix, points, looped_index(first_point - 4))

                            second_point_x = round(second_point_x, 3)
                            second_point_z = round(second_point_z, 3)
                            third_point_x  = round(third_point_x, 3)
                            third_point_z  = round(third_point_z, 3)
                            fourth_point_x = round(fourth_point_x, 3)
                            fourth_point_z = round(fourth_point_z, 3)
                            fifth_point_x  = round(fifth_point_x, 3)
                            fifth_point_z  = round(fifth_point_z, 3)


                            pre_previouse_segment_length = ((zero_point_x - minus_one_point_x) ** 2 + (zero_point_z - minus_one_point_z) ** 2) ** 0.5
                            previouse_segment_length = ((first_point_x - zero_point_x) ** 2 + (first_point_z - zero_point_z) ** 2) ** 0.5

                            # for L and U shaped, calculate length of next wall
                            next_segment_length = ((third_point_x - second_point_x) ** 2 + (third_point_z - second_point_z) ** 2) ** 0.5
                            third_segment_length = ((fourth_point_x - third_point_x) ** 2 + (fourth_point_z - third_point_z) ** 2) ** 0.5

                            previouse_segment_length = round(previouse_segment_length, 3)
                            next_segment_length = round(next_segment_length, 3)
                            third_segment_length = round(third_segment_length, 3)

                            c4d.EventAdd()

                            debug(f"022 - Length to near corner: {final_length}, next_segment_length: {next_segment_length}, third_segment_length: {third_segment_length}")

                            return pre_previouse_segment_length, previouse_segment_length, final_length, next_segment_length, third_segment_length

                    else:
                        debug(f"023 - global_point != near_corner_pos")






# shelving search wall corner
def shelving_extend_to_the_end_of_wall(Rooms_Splines):

    debug('002 - Start extend To the end of wall')

    doc = c4d.documents.GetActiveDocument()

    selected = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)

    for item in selected:

        # collect items data to pass throug function
        selected_item_name, item_pos, item_true_angle, mirroring_by_scale, parent_name = get_selected_item_data(item)

        final_length = 0


        searching_distance = 300
        angle_correction = 180

        match = length_to_the_point(item, selected_item_name, item_pos, item_true_angle, mirroring_by_scale, searching_distance, angle_correction, Rooms_Splines)

        if match != None:

            debug('004 - Point spoted')


            if 'shelving' in selected_item_name:
                debug('005 - Selected item name - ' + selected_item_name)


                #pass_through_pos, pass_through_rotation, mirroring_by_scale, put_detection_distance, put_angle_correction
                pre_previouse_segment_length, previous_segment_length, final_length, next_segment_length, third_segment_length = length_to_the_point(item, selected_item_name, item_pos, item_true_angle, mirroring_by_scale, searching_distance, angle_correction, Rooms_Splines)


                item[c4d.OBJECT_WIDTH] = final_length

                # shelves_fillin(item, length, angle, length_depth, third_segment_length)
                shelves_fillin(item, final_length, next_segment_length, third_segment_length)

                c4d.EventAdd()


            # Bath
            #elif 'Tub' in selected_item_name:
            elif 'tub/shower' in selected_item_name and 'combo tub/shower' not in selected_item_name:
                debug('1005 - Tub/Shower Selected')


                #pass_through_pos, pass_through_rotation, mirroring_by_scale, put_detection_distance, put_angle_correction
                pre_previous_segment_length, previous_segment_length, final_length, next_segment_length, third_segment_length = length_to_the_point(item, selected_item_name, item_pos, item_true_angle, mirroring_by_scale, searching_distance, angle_correction, Rooms_Splines)


                if final_length:
                    debug(f"1006 - Previous segment length: {previous_segment_length}, Final length to the wall corner: {final_length}, next_segment_length: {next_segment_length}, third_segment_length: {third_segment_length}")


                    # length
                    # 150% it is max input, so it is a limit
                    item[c4d.ID_USERDATA,2] = final_length / 60

                    debug(f"1007 - Set length: {item[c4d.ID_USERDATA,2]}")

                    # width

                    width = min(previous_segment_length, next_segment_length)

                    debug([previous_segment_length, next_segment_length])


                    # place shorterst side wall size as width
                    if width < 50:

                        #conversion to persents
                        correction =  35 / 1120
                        final_width = correction * width

                        item[c4d.ID_USERDATA,1] = final_width

                        debug(f"1008 - Set width: {item[c4d.ID_USERDATA,1]}")


                    # for both long walls put default width
                    else:
                        item[c4d.ID_USERDATA,1] = 1

                        debug(f"1008 - Set width: {item[c4d.ID_USERDATA,1]}")


                    c4d.EventAdd()

                    return match



            # Combo Tub/Shower
            elif 'combo tub/shower' in selected_item_name:
                debug('005 - Combo Tub/Shower Selected')

                #pass_through_pos, pass_through_rotation, mirroring_by_scale, put_detection_distance, put_angle_correction
                pre_previous_segment_length, previous_segment_length, final_length, next_segment_length, third_segment_length = length_to_the_point(item, selected_item_name, item_pos, item_true_angle, mirroring_by_scale, searching_distance, angle_correction, Rooms_Splines)


                if final_length:
                    debug(f"2006 - Previous segment length: {previous_segment_length}, Final length to the wall corner: {final_length}, next_segment_length: {next_segment_length}, third_segment_length: {third_segment_length}")


                    #length
                    # 150% it is max input, so it is a limit
                    item[10002] = final_length

                    debug(f"2007 - Set length: {item[10002]}")

                    # width
                    width = min(previous_segment_length, next_segment_length)

                    # place shorterst side wall size as width
                    if width  < 50:
                        item[10003] = width
                    # for both long walls put default width
                    else:
                        pass

                    debug(f"2008 - Set width: {item[10003]}")

                    c4d.EventAdd()

                    return match






            # Shower has other input
            elif 'shower' in selected_item_name and 'combo tub/shower' not in selected_item_name and 'tub/shower' not in selected_item_name:
                debug('3005 - Shower Selected')


                #pass_through_pos, pass_through_rotation, mirroring_by_scale, put_detection_distance, put_angle_correction
                pre_previous_segment_length, previous_segment_length, final_length, next_segment_length, third_segment_length = length_to_the_point(item, selected_item_name, item_pos, item_true_angle, mirroring_by_scale, searching_distance, angle_correction, Rooms_Splines)


                if previous_segment_length:
                    debug(f"3006 - Previous segment length: {previous_segment_length}, Final length to the wall corner: {final_length}, next_segment_length: {next_segment_length}, third_segment_length: {third_segment_length}")


                    # length
                    # 50 it is max input, so it is a limit
                    if final_length> 90:
                        item[c4d.ID_USERDATA,1] = 90
                    else:
                        item[c4d.ID_USERDATA,1] = final_length - 1

                    debug(f"3007 - Set length: {item[c4d.ID_USERDATA,1]}")


                    #width
                    width = min(previous_segment_length, next_segment_length)

                    debug([pre_previous_segment_length, previous_segment_length, final_length, next_segment_length, third_segment_length])
                    for i in range(20):
                        debug(f"width: {width}")


                    if width < 50:
                        item[c4d.ID_USERDATA,2] = width - 0.5
                    else:
                        item[c4d.ID_USERDATA,2] = 40

                    debug(f"3008 - Set width: {item[c4d.ID_USERDATA,2]}")

                    c4d.EventAdd()

                    return match

        else:
            debug('3004 - Point not spoted')
            return

# wall_standing_items_rotation
# for usage in other functions
def for_wall_standing_items(Rooms_Splines):

    try:
        doc = c4d.documents.GetActiveDocument()

        selected = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)
        f_item = selected[0]

        if f_item != None:
            f_item_name = f_item.GetName()
            f_item_name = f_item_name.lower()
        else:
            f_item_name = ''

        if not any(x in f_item_name for x in ('shelving', 'tub', 'shower')):
            return

        threshold = 4





        def get_closest_segment_angle(spline, obj_pos):
            length = c4d.utils.SplineHelp()
            length.InitSpline(spline)
            total_length = length.GetSplineLength()


            closest_distance = float('inf')
            closest_angle = None

            step = 1

            for i in range(0, int(total_length), step):
                pos1 = length.GetPosition(float(i) / total_length)
                pos2 = length.GetPosition(float(i + 1) / total_length)
                p1 = pos1
                p2 = pos2
                segment_center = (p1 + p2) * 0.5

                dist = (obj_pos - segment_center).GetLength()

                if dist < closest_distance:


                    closest_distance = dist
                    direction = (p2 - p1).GetNormalized()
                    angle = math.atan2(direction.z, direction.x)
                    closest_angle = angle + c4d.utils.Rad(180)

            return closest_distance, closest_angle



        if Rooms_Splines:
            Walls_Null = Rooms_Splines.GetUp()
            Walls_Null_children = Walls_Null.GetChildren()
            for Null in Walls_Null_children:

                if Null != None:
                    Null_name = Null.GetName()
                    Null_name = Null_name.lower()
                else:
                    Null_name = ''








        room_splines = Rooms_Splines.GetChildren()
        selected = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)

        angle = c4d.utils.Rad(0)
        spline_name = ''


        for f_item in selected:

            obj_pos= fix_matrix(f_item)


            #for spline in room_splines:
            for spline in chain(room_splines):


                # ignore primitive objects - circles, rectangle, ect
                if spline and spline.GetType() != c4d.Ospline:
                    continue


                if spline[c4d.ID_BASEOBJECT_GENERATOR_FLAG] == False:
                    continue

                if spline != None:
                    spline_name_wall_standing = spline.GetName()
                    spline_name_wall_standing = spline_name_wall_standing.lower()
                else:
                    spline_name_wall_standing = ''


                sh = SplineHelp()
                sh.InitSpline(spline)

                spline_length = sh.GetSplineLength()

                if spline_length < 250:
                    continue

                points = spline.GetAllPoints()
                if not points:
                    continue

                amount_of_points = len(spline.GetAllPoints())






                dist, angle = get_closest_segment_angle(spline, obj_pos)

                if dist is not None and dist <= threshold:


                    #spline_name_wall_standing = spline.GetName()


                    spline_parent = spline.GetUp()

                    if spline_parent != None:
                        spline_parent_name = spline_parent.GetName()
                        spline_parent_name = spline_parent_name.lower()
                    else:
                        spline_parent_name = ''

                    if 'bar' in spline_name_wall_standing or 'wall' in spline_name_wall_standing:
                        angle += c4d.utils.Rad(180)# or 'Bar Counter' in spline_parent_name:

                    if 'tub/shower' in f_item_name:
                        angle += c4d.utils.Rad(90)

                    if 'combo tub/shower' in f_item_name:
                        angle -= c4d.utils.Rad(90)

                    angle_wall_standing = angle + parents_rotation(f_item)

                    f_item[c4d.ID_BASEOBJECT_REL_ROTATION, c4d.VECTOR_X] = angle_wall_standing

                    return angle_wall_standing, spline_name_wall_standing


    except:
        print("An error occurred:")
        traceback.print_exc()













# main
def main():

    doc = c4d.documents.GetActiveDocument()


    Rooms_Splines = None

    # new projects
    Main_Null = doc.SearchObject('3D Floor Plan')
    if Main_Null:
        Outer_Null = Main_Null.GetDown().GetDown().GetDown()
        Rooms_Splines = Outer_Null.GetNext()


    # predesign projects
    if not Rooms_Splines or not Rooms_Splines.GetDown():
        possible_null_names = ['SPLINES', 'Splines', 'splines', 'Create Outline Reference']
        for name in possible_null_names:
            folder = doc.SearchObject(name)
            if folder and folder.CheckType(c4d.Onull) and folder.GetDown():
                Rooms_Splines = folder
                break

    if not Rooms_Splines:
        message = f'Rooms_Splines not found.'
        c4d.gui.MessageDialog(message)



    doc.StartUndo()

    # run automation
    debug('')
    debug('001 - Start main automation')

    for_wall_standing_items(Rooms_Splines)
    shelving_extend_to_the_end_of_wall(Rooms_Splines)

    corner_spoted = automation_by_hovering_on_corners(Rooms_Splines)
    if corner_spoted == True:
        automation_by_hovering_on_corners(Rooms_Splines)

    doc.EndUndo()
    c4d.EventAdd()








# Execute main()
if __name__=='__main__':
    main()