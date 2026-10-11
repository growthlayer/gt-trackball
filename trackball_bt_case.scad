// ============================================================
//  Bluetooth Arcade Trackball Case  (v2)
//  Remix/upgrade of Thingiverse thing:7334881 (vkschannel),
//  itself a remix of thing:5914322 (dotBtty).
//  License: CC BY-SA (inherited)
//
//  Improvements over the original:
//   * Trackball interface copied exactly from the original: four
//     Ø5.1 locating pins into the trackball's mounting holes, clamped
//     floor-to-ceiling; bottom plate now screws into M3 brass inserts
//   * 3 button holes (left / menu / right)
//   * Ergonomic chamfered palm slope on the front
//   * Flush deck window for Waveshare Pico-ePaper-2.13 with
//     Pi Pico 2 W plugged on its back (mounted from inside)
//   * Mounts for TP4056 charger, boost module, LiPo pouch tray; one
//     USB-A D-type feedthrough (wired mode + charging); no power switch
//   * Rubber feet recesses, ventilation slots
//
//  PRINTING
//   part="top"      -> print upside down (as exported), no supports
//   part="bottom"   -> print as-is, no supports
//   part="clips"    -> two e-ink retainer clips, print as-is
//   part="template" -> quick fit-check plate, PRINT ME FIRST
//   part="assembly" -> on-screen preview only
// ============================================================

part = "assembly";   // ["top","bottom","clips","template","assembly","exploded","layout","shell"]

// ---------- MEASURE-ME parameters -----------------------------------
// Verify these against YOUR trackball unit with calipers before the
// big print. The defaults reproduce the proven fit of thing:7334881.

ball_opening_d   = 76.1;   // top opening the ball pokes through —
                           // straight bore, exactly as the original
// Locating pins, copied from the original: solid Ø5.1 x 18.5 pins hang
// from the deck underside and drop into the trackball's four mounting
// holes. The trackball's 80.5 mm hole square sits turned 45° in the case,
// so the holes land on the axes at r = 56.6. Its hole surface presses the
// deck underside and it is clamped from below by the bottom plate.
plate_drop       = 18.5;   // pin length below the deck underside
pin_d            = 5.1;
plate_holes      = [[56.6,0],[0,56.6],[-56.6,0],[0,-56.6]];
plate_screwhead_recess = true;   // 20mm dia relief pockets
screwhead_pos    = [[45,45],[-45,45],[45,-45],[-45,-45]];
body_w           = 140;    // trackball body (below plate) width  X
body_d           = 140;    // trackball body depth Y
button_hole_d    = 29.3;   // matches the original case's button holes

// ---------- main case dimensions ------------------------------------
wall        = 3.0;
top_t       = 4.5;         // top skin thickness
H           = 72.1;        // overall shell height (as original)
inner_x     = 97.5;        // interior half-width: >= the original's
                           // measured walls (-94.1 .. +97.5 from ball)
inner_fy    = -75.5;       // interior front edge (original: -75.5)
inner_ry    = 143.5;       // interior rear edge: the display PCB sits
                           // behind the MENU button's body
corner_r    = 8;           // vertical edge rounding
top_round_r = 3;           // roundover on the outer top edges
chamfer_drop  = 13;        // front palm bevel size (45 deg so the
                           // upside-down print needs no supports)
bevel_round_r = 4;         // roundover on the bevel's two creases
                           // (bevel-to-deck and bevel-to-front-wall)

// ---------- buttons --------------------------------------------------
// left / menu / right: the original's three holes, exact positions
button_pos  = [[-53.4,90.5],[0,90.5],[53.4,90.5]];
button_keepout_r = 16.5;   // snap-in button body under the deck + 1 mm

// ---------- fasteners ------------------------------------------------
insert_d    = 4.2;   // hole for M3 x L4 x D5.0 heat-set inserts
insert_h    = 5.5;   // insert length + 1.5
lid_screw_d = 3.4;   // M3 clearance; screws into pillar inserts
lid_screw_head = 6.5;
pillar_d    = 12;

// ---------- electronics ----------------------------------------------
// Waveshare Pico-ePaper-2.13 (Pico 2 W plugged on the back)
// per Waveshare's mechanical spec: outline 65.0 x 30.5, panel 48.55 x 23.70
epd_pcb_w   = 65.0;  epd_pcb_h = 30.5;  epd_pcb_t = 1.8;
epd_win_w   = 50.0;  epd_win_h = 25.0;  // visible window
epd_stack_t = 16;    // display PCB + Pico + headers, total thickness
epd_center  = [0, 90.5 + 16.5 + 1 + 30.5/2];  // PCB clears MENU body
epd_flex_extra = 6;                     // pocket allowance, flex-cable side (+X)
clip_screw_d = 2.0;                     // M2.5 self-tap pilot
clip_screw_x = epd_pcb_w/2 + epd_flex_extra + 5;  // clip screw offset
clip_pad_h  = epd_pcb_t + 0.2;          // pad face flush with PCB back

// TP4056 charger (USB-C version)
// its USB-C port is internal/unused -- charge power comes in on wires
// from the Pico's VBUS pin (see wiring.svg)
tp_w = 24;    tp_l = 19;   tp_center = [-inner_x + 24/2 + 6, 107];
// ONE external port: a D-type USB-A female/female feedthrough in the rear
// wall, front-mounted (flange outside, M3 screws through slots, nuts
// inside). Inside, the Pico's micro-USB-to-A cable plugs into it. The PC's
// USB-A cable then runs the wired mouse AND charges: the Pico's VBUS pin
// is wired to the TP4056 input. The TP4056's own USB-C stays internal.
// Sits between the MENU and RIGHT buttons -- the only spot where the
// internal A plug passes between the button bodies.
// Per the module's drawing: body hole Ø23.7; two Ø3.4 mounting holes on a
// DIAGONAL (top-left / bottom-right as seen from outside), 19 mm apart
// horizontally and 24 mm vertically. Front-mounted: flange outside, M3
// screws self-thread into Ø2.6 pilots in the 3 mm wall.
usb_ft_center_x = 26.7;
usb_ft_center_z = 36;
usb_ft_body_d   = 24.4;     // Ø23.7 body + 0.7 clearance
usb_ft_hole_dx  = 19;       // horizontal hole spacing
usb_ft_hole_dz  = 24;       // vertical hole spacing
usb_ft_pilot_d  = 2.6;      // M3 self-tapping pilot

// MT3608 boost module (not used: the charger board boosts). Its pegs now
// hold the MOSFET trigger module.
boost_w = 17;  boost_l = 30;  boost_center = [80.5, 107]; // floor, right-rear

// (no power switch: the controller sleeps in firmware and wakes on a
//  button press or ball movement; the battery is always connected)

// battery: flat LiPo pouch lying on the rear-bay floor (52 x 35 x 10).
// bat_w is the X extent, bat_l the Y extent.
bat_w = 52;  bat_l = 35;  bat_h = 10;  bat_center = [0, 95];
bat_wall = 1.5;  bat_wall_h = 7;   // tray walls (pack stands proud, zip-tied)
bat_clr  = 0.5;                    // per side

// Raspberry Pi Pico 2 W on standoffs, rear-bay floor behind the battery.
// Pico PCB 51 x 21; its 4 mounting holes are 47 x 11.4 apart.
pico_center = [0, 130];  pico_pcb_w = 51;  pico_pcb_l = 21;
pico_hole_dx = 47;  pico_hole_dy = 11.4;
// Mounted UPSIDE DOWN (components toward the plate) so the long header
// pins point up and the jumpers plug in from above. The micro-USB jack
// then sits between the two end standoffs, under the board.
pico_standoff_h = 8;     // micro-USB plug overmold hangs ~4 below the PCB
pico_usb_gap    = 8.4;   // flat-to-flat between standoffs (jack is 7.5-8 wide)
pico_usb_flat_h = 3.2;   // D-flat only where the jack is (top of standoff)
pico_screw_d = 1.6;      // M2 self-tap pilot

// ---------- bottom plate ---------------------------------------------
plate_t    = 3.7;
// feet: 3M Bumpon SJ5312 (cylindrical, 12.7 dia x 3.5 tall) in corner
// recesses -- project standard shared with the pinball controller
foot_d     = 13.0;  foot_recess = 1.2;

$fn = 96;
eps = 0.01;

// ============================================================
//  helpers
// ============================================================
module rbox(x0,y0,x1,y1,h,r=corner_r){   // rounded-corner box
  hull()
    for(p=[[x0+r,y0+r],[x1-r,y0+r],[x0+r,y1-r],[x1-r,y1-r]])
      translate([p[0],p[1],0]) cylinder(r=r,h=h);
}

// corner post with a rounded top rim (radius rt), for rbox_roundtop
module round_post(r,h,rt){
  rotate_extrude()
    union(){
      square([r, h-rt]);
      square([r-rt, h]);
      translate([r-rt, h-rt]) circle(r=rt);
    }
}
// rounded-corner box whose top outer edges are rounded over by rt
module rbox_roundtop(x0,y0,x1,y1,h,r=corner_r,rt=top_round_r){
  hull()
    for(p=[[x0+r,y0+r],[x1-r,y0+r],[x0+r,y1-r],[x1-r,y1-r]])
      translate([p[0],p[1],0]) round_post(r,h,rt);
}

function outer_fx() = -inner_x - wall;
function outer_rx() =  inner_x + wall;
function outer_fy() =  inner_fy - wall;
function outer_ry() =  inner_ry + wall;
ceil_z   = H - top_t;               // interior ceiling
datum_z  = H - top_t - plate_drop;  // locating-pin tips

function pillar_pos() = [
  [-inner_x+pillar_d/2-1, inner_fy+pillar_d/2-1],
  [ inner_x-pillar_d/2+1, inner_fy+pillar_d/2-1],
  [-inner_x+pillar_d/2-1, inner_ry-pillar_d/2+1],
  [ inner_x-pillar_d/2+1, inner_ry-pillar_d/2+1]];

// front palm bevel cutter: 45-degree plane through the top front edge.
// dz raises the plane vertically; pass -top_t*sqrt(2) for the cavity to
// get a parallel plane offset inward by the skin thickness (same slope!).
module chamfer_cut(dz=0){
  y0 = outer_fy() - 1;
  L  = 120;
  translate([outer_fx()-1, 0, 0])
  rotate([90,0,90])
  linear_extrude(2*(inner_x+wall)+2)
    polygon([[y0, H - chamfer_drop + dz],
             [y0 + L, H - chamfer_drop + dz + L],
             [y0 + L, H + 200],
             [y0, H + 200]]);
}

// keep-side prism of the case's front profile: vertical wall, tangent
// arc (R), 45-deg bevel, tangent arc (R), flat deck. Intersect the
// outer solid with this to get a bevel whose two creases are true
// convex roundovers.
module front_profile_prism(R=bevel_round_r){
  t  = R*tan(22.5);
  yF = outer_fy();
  pts = concat(
    [[yF, -1], [yF, H-chamfer_drop-t]],
    // bottom crease arc: center (yF+R, H-chamfer_drop-t)
    [for(a=[175:-5:140]) [yF+R + R*cos(a), H-chamfer_drop-t + R*sin(a)]],
    // top crease arc: center (yF+chamfer_drop+t, H-R)
    [for(a=[130:-5:95]) [yF+chamfer_drop+t + R*cos(a), H-R + R*sin(a)]],
    [[yF+chamfer_drop+t, H], [outer_ry()+10, H], [outer_ry()+10, -1]]
  );
  translate([outer_fx()-1, 0, 0])
  rotate([90,0,90])
  linear_extrude(2*(inner_x+wall)+2)
    polygon(pts);
}

// ============================================================
//  TOP SHELL
// ============================================================
module top_shell(){
  difference(){
    union(){
      // outer solid (rounded prism ∩ front profile) minus cavity
      difference(){
        intersection(){
          rbox_roundtop(outer_fx(),outer_fy(),outer_rx(),outer_ry(),H);
          front_profile_prism();
        }
        difference(){
          translate([0,0,-1])
            rbox(-inner_x,inner_fy,inner_x,inner_ry,ceil_z+1,r=corner_r-wall/2);
          // cavity plane sits BELOW the outer bevel by the skin thickness
          chamfer_cut(-top_t*sqrt(2));
        }
      }
      // locating pins into the trackball's mounting holes (as original)
      for(p=plate_holes)
        translate([p[0],p[1],datum_z]) cylinder(d=pin_d,h=plate_drop+eps);
      // bottom-plate corner pillars (overlap into the walls);
      // cone on top so the upside-down print has no flat overhang
      for(p=pillar_pos())
        translate([p[0],p[1],plate_t]){
          cylinder(d=pillar_d,h=28);
          translate([0,0,28-eps]) cylinder(d1=pillar_d,d2=2,h=pillar_d/2);
        }
      // e-ink retainer clip pads under the deck (face flush with PCB back)
      for(sx=[-1,1])
        translate([sx*clip_screw_x, epd_center[1], ceil_z-clip_pad_h])
          cylinder(d=9,h=clip_pad_h+eps);
    }
    // ---- subtractions ----
    // ball opening — straight bore, identical to the original (no
    // chamfer: the surface-level diameter is part of the proven fit)
    translate([0,0,ceil_z-eps]) cylinder(d=ball_opening_d,h=top_t+2*eps);
    // button holes
    for(b=button_pos)
      translate([b[0],b[1],ceil_z-eps]) cylinder(d=button_hole_d,h=top_t+10);
    // screw-head relief pockets in the ceiling
    if(plate_screwhead_recess)
      for(p=screwhead_pos)
        translate([p[0],p[1],ceil_z-0.6]) cylinder(d=20,h=0.7);
    // M3 heat-set insert pockets in the pillar ends (bottom plate screws)
    for(p=pillar_pos())
      translate([p[0],p[1],plate_t-eps]) cylinder(d=insert_d,h=insert_h);
    // --- e-ink display: window + bezel chamfer + PCB pocket ---
    translate([epd_center[0],epd_center[1],0]){
      translate([-epd_win_w/2,-epd_win_h/2,ceil_z-eps])
        cube([epd_win_w,epd_win_h,top_t+2*eps]);
      // cosmetic bezel chamfer on the outside
      hull(){
        translate([-epd_win_w/2,-epd_win_h/2,H-1]) cube([epd_win_w,epd_win_h,1+eps]);
        translate([-epd_win_w/2-2,-epd_win_h/2-2,H+eps]) cube([epd_win_w+4,epd_win_h+4,eps]);
      }
      // PCB pocket from below (edge-grip; flex-cable allowance on +X)
      translate([-epd_pcb_w/2-0.4, -epd_pcb_h/2-0.4, ceil_z-epd_pcb_t-0.2])
        cube([epd_pcb_w+0.8+epd_flex_extra, epd_pcb_h+0.8, epd_pcb_t+0.2+eps]);
    }
    // clip screw pilots
    for(sx=[-1,1])
      translate([sx*clip_screw_x, epd_center[1], ceil_z-clip_pad_h-eps])
        cylinder(d=clip_screw_d,h=clip_pad_h+3.5);
    // D-type USB-A feedthrough in the rear wall: body hole + diagonal pilots.
    // Seen from OUTSIDE the rear wall, case +x is on the viewer's left, so
    // "top-left" = (+x, +z) and "bottom-right" = (-x, -z).
    translate([usb_ft_center_x, inner_ry-1, usb_ft_center_z]) rotate([-90,0,0]){
      cylinder(d=usb_ft_body_d, h=wall+2);
      for(sg=[1,-1])
        translate([sg*usb_ft_hole_dx/2, -sg*usb_ft_hole_dz/2, 0])
          cylinder(d=usb_ft_pilot_d, h=wall+2);
    }
  }
}

// ============================================================
//  BOTTOM PLATE  (with battery cradle + board rails)
// ============================================================
// retainer posts on a PCB's four edges (cl = clearance per side), inset
// from the corners; skip_xneg / skip_xpos leave that short edge open
// (case wall does the job, or a connector needs the room).
module board_posts(c, w, l, inset=3, skip_xneg=false, skip_xpos=false, cl=0.3){
  r=2.5; h=plate_t+4;
  for(sy=[-1,1], fx=[-1,1])
    translate([c[0]+fx*(w/2-inset), c[1]+sy*(l/2+cl+r), 0]) cylinder(r=r,h=h);
  for(sx=[-1,1], fy=[-1,1]) if(!(skip_xneg && sx<0) && !(skip_xpos && sx>0))
    translate([c[0]+sx*(w/2+cl+r), c[1]+fy*(l/2-inset), 0]) cylinder(r=r,h=h);
}

// Internal zip-tie anchors at both ends of the battery tray: a bridge the
// tie loops under, all on the inside. Tie path: over the pack, down the
// gap between tray wall and anchor, under the bridge, up and back over.
// Optional -- a strip of double-sided foam tape in the tray also works.
anchor_gap = 3;  anchor_len = 4.5;  anchor_w = 10;
anchor_tunnel_w = 6;  anchor_tunnel_h = 2.5;  anchor_h = 4.5;
module tie_anchors(){
  bw = bat_w + 2*bat_clr + 2*bat_wall;
  for(sx=[-1,1])
    translate([bat_center[0] + sx*(bw/2 + anchor_gap + anchor_len/2), bat_center[1], 0])
      difference(){
        translate([-anchor_len/2, -anchor_w/2, 0]) cube([anchor_len, anchor_w, plate_t+anchor_h]);
        translate([-anchor_len/2-1, -anchor_tunnel_w/2, plate_t-eps])
          cube([anchor_len+2, anchor_tunnel_w, anchor_tunnel_h+eps]);
      }
}

module bottom_plate(){
  clr = 0.25;
  difference(){
    union(){
      rbox(-inner_x+clr,inner_fy+clr,inner_x-clr,inner_ry-clr,plate_t,r=corner_r-wall/2);
      // --- battery tray: four low walls around the flat pack ---
      let(bw=bat_w+2*bat_clr, bl=bat_l+2*bat_clr){
        for(sx=[-1,1])
          translate([bat_center[0]+sx*(bw/2+bat_wall/2)-bat_wall/2,
                     bat_center[1]-bl/2-bat_wall, 0])
            cube([bat_wall, bl+2*bat_wall, bat_wall_h+plate_t]);
        for(sy=[-1,1])
          translate([bat_center[0]-bw/2-bat_wall,
                     bat_center[1]+sy*(bl/2+bat_wall/2)-bat_wall/2, 0])
            cube([bw+2*bat_wall, bat_wall, bat_wall_h+plate_t]);
      }
      // --- Pico standoffs (screwed down through its 4 mounting holes) ---
      // top pico_usb_flat_h is D-flattened on the inner face so the
      // (downward-facing) micro-USB jack fits between the end pair
      for(sx=[-1,1],sy=[-1,1])
        translate([pico_center[0]+sx*pico_hole_dx/2,
                   pico_center[1]+sy*pico_hole_dy/2, 0])
          difference(){
            cylinder(d=5,h=pico_standoff_h+plate_t);
            translate([-3, sy>0 ? -pico_hole_dy/2-10+pico_usb_gap/2 : pico_hole_dy/2-pico_usb_gap/2,
                       plate_t+pico_standoff_h-pico_usb_flat_h])
              cube([6,10,pico_usb_flat_h+1]);
          }
      tie_anchors();
      // charger: USB-C end faces +X (toward the battery) and is left open
      // so a USB-C plug fits; 0.6 clearance -- 0.3 was too tight in print
      board_posts(tp_center, tp_w, tp_l, inset=4, skip_xpos=true, cl=0.6);
      // inset 2 keeps the short-end posts clear of the centered micro-USB
      board_posts(boost_center, boost_w, boost_l, inset=2);
    }
    // countersunk M3 screws at the corners (heads on the underside)
    for(p=pillar_pos()){
      translate([p[0],p[1],-eps]) cylinder(d=lid_screw_d,h=plate_t+2*eps);
      translate([p[0],p[1],-eps]) cylinder(d1=lid_screw_head+0.4,d2=lid_screw_d,h=1.8+eps);
    }
    // rubber feet recesses (underside) -- 3M Bumpon SJ5312
    for(p=[[-inner_x+20,inner_fy+20],[inner_x-20,inner_fy+20],
           [-inner_x+20,inner_ry-20],[inner_x-20,inner_ry-20]])
      translate([p[0],p[1],-eps]) cylinder(d=foot_d,h=foot_recess);
    // Pico screw pilots
    for(sx=[-1,1],sy=[-1,1])
      translate([pico_center[0]+sx*pico_hole_dx/2,
                 pico_center[1]+sy*pico_hole_dy/2, plate_t])
        cylinder(d=pico_screw_d,h=pico_standoff_h+eps);
    // ventilation slots, kept clear of the battery tray and boards
    for(sx=[-1,1]) for(i=[0:3])
      translate([sx*(42+i*6)-2, 78, -eps]) cube([3, 26, plate_t+2*eps]);
    // (no through-slots: nothing shows on the underside; see tie_anchors)
  }
}

// ============================================================
//  E-INK RETAINER CLIPS (press the display PCB into its pocket)
// ============================================================
// flat bar: screw end sits on the pad, the other end presses the PCB
// (pad face is flush with the PCB back, so a flat bar bridges both)
module eink_clip(){
  difference(){
    hull(){ cylinder(d=9,h=2.5); translate([-16,0,0]) cylinder(d=8,h=2.5); }
    translate([0,0,-eps]) cylinder(d=2.8,h=10);  // M2.5 clearance
  }
}

// ============================================================
//  FIT-CHECK TEMPLATE  (print me first!)
// ============================================================
module fit_template(){
  difference(){
    union(){
      rbox(outer_fx(),outer_fy(),outer_rx(),outer_ry(),2.4);
    }
    translate([0,0,-eps]) cylinder(d=ball_opening_d,h=3);
    for(p=plate_holes) translate([p[0],p[1],-eps]) cylinder(d=pin_d+0.4,h=20);
    for(b=button_pos)  translate([b[0],b[1],-eps]) cylinder(d=button_hole_d,h=3);
    if(plate_screwhead_recess)
      for(p=screwhead_pos) translate([p[0],p[1],-eps]) cylinder(d=20,h=0.6);
    // display window position check
    translate([epd_center[0]-epd_win_w/2, epd_center[1]-epd_win_h/2, -eps])
      cube([epd_win_w,epd_win_h,3]);
    // lighten it
    for(a=[45:90:315])
      rotate([0,0,a]) translate([74,0,-eps]) cylinder(d=22,h=3);
  }
}

// ============================================================
//  COMPONENT LAYOUT VIEW (documentation render, not printable)
// ============================================================
module label(txt, s=6){
  color("Black") linear_extrude(0.6)
    text(txt, size=s, halign="center", valign="center", font="Arial:style=Bold");
}
module mockbox(c, size, col, txt="", ts=5){
  color(col) translate([c[0]-size[0]/2, c[1]-size[1]/2, plate_t]) cube(size);
  if(txt!="") translate([c[0], c[1], plate_t+size[2]+0.5]) label(txt, ts);
}
btn_names = ["LEFT","MENU","RIGHT"];

// exploded assembly (documentation render): parts in assembly order,
// pulled apart along Z
explode = [0, 95, 200, 290, 360];   // plate+electronics, trackball, display, shell, buttons
module exploded(){
  // 1. bottom plate with the electronics and feet
  color("LightSteelBlue") bottom_plate();
  mockbox(bat_center,[bat_w,bat_l,bat_h],"MediumSeaGreen");
  mockbox(tp_center,[tp_w,tp_l,5],"IndianRed");
  mockbox(boost_center,[boost_w,boost_l,7],"Orange");
  mockbox([-84,75],[13,27,6],"Teal");
  color("ForestGreen")
    translate([pico_center[0]-pico_pcb_w/2, pico_center[1]-pico_pcb_l/2, plate_t+pico_standoff_h])
      cube([pico_pcb_w,pico_pcb_l,1.6]);
  for(p=[[-inner_x+20,inner_fy+20],[inner_x-20,inner_fy+20],[-inner_x+20,inner_ry-20],[inner_x-20,inner_ry-20]])
    color("DimGray") translate([p[0],p[1],-18]) cylinder(d=12.7,h=3.5);
  // 2. trackball: housing turned 45 degrees, arms into the corners
  translate([0,0,explode[1]]) {
    color("DimGray") rotate([0,0,45]) translate([-35,-100,0]) cube([70,200,10]);
    color("DimGray") rotate([0,0,-45]) translate([-35,-100,0]) cube([70,200,10]);
    color("DimGray") translate([0,0,0]) cylinder(d=110,h=48);
    color("Gold") translate([0,0,52]) sphere(d=76.2);
  }
  // 3. e-paper display + its two clips (sit under the deck window)
  translate([0,0,explode[2]]) {
    color("MediumPurple") translate([epd_center[0]-epd_pcb_w/2, epd_center[1]-epd_pcb_h/2, 0])
      cube([epd_pcb_w,epd_pcb_h,1.6]);
    color("WhiteSmoke") translate([epd_center[0]-24, epd_center[1]-11.5, 1.6]) cube([48,23,1]);
    for(sx=[-1,1]) color("LightSteelBlue")
      translate([epd_center[0]+sx*(epd_pcb_w/2+4), epd_center[1], -8]) rotate([0,0,sx>0?0:180]) eink_clip();
  }
  // 4. top shell
  translate([0,0,explode[3]-H+20]) color("SteelBlue") top_shell();
  // 5. buttons + the USB-A feedthrough
  for(b=button_pos) translate([b[0],b[1],explode[4]]) {
    color("WhiteSmoke") cylinder(d=24,h=10);
    color("Silver") translate([0,0,-2]) cylinder(d=33,h=2);
    color("Silver") translate([0,0,-38]) cylinder(d=24,h=36);
  }
  color("IndianRed") translate([usb_ft_center_x, inner_ry+wall+45, explode[3]-H+20+usb_ft_center_z])
    rotate([90,0,0]) cylinder(d=23.7,h=20);
}
module layout(){
  bottom_plate();
  // wall footprint ring
  color("SteelBlue") difference(){
    rbox(outer_fx(),outer_fy(),outer_rx(),outer_ry(),3);
    translate([0,0,-1]) rbox(-inner_x,inner_fy,inner_x,inner_ry,5,r=corner_r-wall/2);
  }
  // trackball body + ball
  color("DimGray") translate([-body_w/2,-body_d/2,plate_t]) cube([body_w,body_d,45]);
  color("WhiteSmoke") translate([0,0,plate_t+45]) sphere(d=76.2);
  translate([0,-48,90]) label("TRACKBALL",7);
  // battery (flat LiPo pouch)
  mockbox(bat_center,[bat_w,bat_l,bat_h],"MediumSeaGreen");
  translate([bat_center[0],bat_center[1],plate_t+bat_h+1]) label("LiPo 52x35",5);
  mockbox(tp_center,[tp_w,tp_l,5],"IndianRed","CHG",4.5);
  // MOSFET module in the spare right-rear pegs, battery sensor beside the
  // trackball near the charger (both hot-glued; sizes approximate)
  mockbox(boost_center,[boost_w,boost_l,7],"Orange","FET",4.5);
  mockbox([-84,75],[13,27,6],"Teal","V",4.5);
  // e-ink display hanging under the deck (wired, not stacked on the Pico)
  color("MediumPurple")
    translate([epd_center[0]-epd_pcb_w/2, epd_center[1]-epd_pcb_h/2, ceil_z-10])
      cube([epd_pcb_w,epd_pcb_h,10]);
  translate([epd_center[0],epd_center[1],ceil_z+1]) label("E-INK",4.5);
  // Pico 2 W on standoffs, rear-bay floor
  color("SteelBlue")
    translate([pico_center[0]-pico_pcb_w/2, pico_center[1]-pico_pcb_l/2,
               plate_t+pico_standoff_h])
      cube([pico_pcb_w,pico_pcb_l,12]);
  translate([pico_center[0],pico_center[1],plate_t+pico_standoff_h+13])
    label("PICO 2 W",5);
  // buttons
  for(i=[0:2]){
    b=button_pos[i];
    color("Gold") translate([b[0],b[1],ceil_z-20]) cylinder(d=button_hole_d+4,h=20);
    translate([b[0],b[1],ceil_z+1]) label(btn_names[i],5);
  }
  // USB-A feedthrough marker outside the rear wall
  color("IndianRed") translate([usb_ft_center_x, inner_ry+wall+1.5, usb_ft_center_z]) cube([26.4,3,31],center=true);
  translate([usb_ft_center_x, inner_ry+wall+10, 3]) label("USB-A",4.5);
}

// ---- interference checks: each should render EMPTY ----
module button_bodies(){
  for(b=button_pos) translate([b[0],b[1],ceil_z-40]) cylinder(r=button_keepout_r-1,h=40-eps);
}
module usb_ft_inside(){   // coupler body inside the wall + the A plug and overmold
  translate([usb_ft_center_x, inner_ry, usb_ft_center_z]) rotate([90,0,0]) cylinder(d=24,h=21);
  translate([usb_ft_center_x-6, inner_ry-21-19, usb_ft_center_z-4]) cube([12,19,8]);
}
module mock_parts(){   // real component envelopes as installed
  translate([tp_center[0]-tp_w/2, tp_center[1]-tp_l/2, plate_t+0.05]) cube([tp_w,tp_l,1.6]);
  translate([boost_center[0]-boost_w/2, boost_center[1]-boost_l/2, plate_t+0.05]) cube([boost_w,boost_l,1.6]);
  translate([bat_center[0]-bat_w/2, bat_center[1]-bat_l/2, plate_t+0.05]) cube([bat_w,bat_l,bat_h]);
  translate([pico_center[0]-pico_pcb_w/2, pico_center[1]-pico_pcb_l/2, plate_t+pico_standoff_h+0.05])
    cube([pico_pcb_w,pico_pcb_l,12]);
  button_bodies();
  usb_ft_inside();
}

// ============================================================
//  part selection
// ============================================================
if(part=="top")          translate([0,0,H]) rotate([180,0,0]) top_shell();  // print upside down
else if(part=="bottom")  bottom_plate();
else if(part=="clips")   for(i=[0,1]) translate([0,i*14,0]) eink_clip();
else if(part=="template")fit_template();
else if(part=="layout")  layout();
else if(part=="xsection")                       // front-profile check
  intersection(){ top_shell(); translate([-1,-200,-1]) cube([2,400,200]); }
// interference checks: each must render EMPTY
else if(part=="chk_shell_plate") intersection(){ top_shell(); bottom_plate(); }
else if(part=="chk_parts_plate") intersection(){ bottom_plate(); mock_parts(); }
else if(part=="chk_parts_shell") intersection(){ top_shell(); mock_parts(); }
else if(part=="chk_usb_buttons") intersection(){ usb_ft_inside(); button_bodies(); }
else if(part=="exploded") exploded();
else if(part=="shell")   top_shell();                 // assembled position (renders)
else {                    // assembly preview
  color("SteelBlue")  top_shell();
  color("LightSteelBlue") bottom_plate();
  // ghost of the trackball plate + ball + display
  %translate([0,0,ceil_z-10]) sphere(d=76.2);
  %translate([epd_center[0],epd_center[1],ceil_z-1]) cube([epd_pcb_w,epd_pcb_h,epd_pcb_t],center=true);
}
