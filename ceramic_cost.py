"""
세라믹 가공비 계산 프로그램 v3
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json, os, math

SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ceramic_cost_data.json")

class Shape:
    _id_counter = 0
    def __init__(self, kind):
        Shape._id_counter += 1
        self.id = Shape._id_counter
        self.kind = kind
        self.selected = False
    def perimeter_mm(self): return 0.0
    def to_dict(self): return {}
    @staticmethod
    def from_dict(d):
        k = d.get("kind")
        m = {"rect": RectShape, "circle": CircleShape,
             "ellipse": EllipseShape, "hole": HoleShape, "line": LineShape}
        cls = m.get(k)
        return cls.from_dict(d) if cls else None

class RectShape(Shape):
    def __init__(self, x=10, y=10, w=50, h=30):
        super().__init__("rect")
        self.x=x; self.y=y; self.w=w; self.h=h
    def perimeter_mm(self): return 2*(self.w+self.h)
    def to_dict(self): return {"kind":"rect","x":self.x,"y":self.y,"w":self.w,"h":self.h}
    @staticmethod
    def from_dict(d): return RectShape(d["x"],d["y"],d["w"],d["h"])

class CircleShape(Shape):
    def __init__(self, cx=30, cy=30, r=20):
        super().__init__("circle")
        self.cx=cx; self.cy=cy; self.r=r
    def perimeter_mm(self): return 2*math.pi*self.r
    def to_dict(self): return {"kind":"circle","cx":self.cx,"cy":self.cy,"r":self.r}
    @staticmethod
    def from_dict(d): return CircleShape(d["cx"],d["cy"],d["r"])

class EllipseShape(Shape):
    def __init__(self, cx=40, cy=30, rx=30, ry=15):
        super().__init__("ellipse")
        self.cx=cx; self.cy=cy; self.rx=rx; self.ry=ry
    def perimeter_mm(self):
        a,b=self.rx,self.ry
        return math.pi*(3*(a+b)-math.sqrt((3*a+b)*(a+3*b)))
    def to_dict(self): return {"kind":"ellipse","cx":self.cx,"cy":self.cy,"rx":self.rx,"ry":self.ry}
    @staticmethod
    def from_dict(d): return EllipseShape(d["cx"],d["cy"],d["rx"],d["ry"])

class HoleShape(Shape):
    def __init__(self, cx=30, cy=30, r=5):
        super().__init__("hole")
        self.cx=cx; self.cy=cy; self.r=r
    def perimeter_mm(self): return 2*math.pi*self.r
    def to_dict(self): return {"kind":"hole","cx":self.cx,"cy":self.cy,"r":self.r}
    @staticmethod
    def from_dict(d): return HoleShape(d["cx"],d["cy"],d["r"])

class LineShape(Shape):
    def __init__(self, x1=10, y1=10, x2=60, y2=10):
        super().__init__("line")
        self.x1=x1; self.y1=y1; self.x2=x2; self.y2=y2
    def perimeter_mm(self): return math.hypot(self.x2-self.x1,self.y2-self.y1)
    def to_dict(self): return {"kind":"line","x1":self.x1,"y1":self.y1,"x2":self.x2,"y2":self.y2}
    @staticmethod
    def from_dict(d): return LineShape(d["x1"],d["y1"],d["x2"],d["y2"])

class SnapSystem:
    ENDPOINT="endpoint"; MIDPOINT="midpoint"; CENTER="center"; GRID="grid"
    def __init__(self):
        self.tol_px=12; self.grid_size=5.0
        self.grid_snap=True; self.object_snap=True
    def snap_points(self, shapes):
        pts=[]
        for s in shapes:
            if s.kind=="rect":
                x,y,w,h=s.x,s.y,s.w,s.h
                for p in [(x,y),(x+w,y),(x+w,y+h),(x,y+h)]:
                    pts.append((p,self.ENDPOINT))
                for p in [(x+w/2,y),(x+w,y+h/2),(x+w/2,y+h),(x,y+h/2)]:
                    pts.append((p,self.MIDPOINT))
                pts.append(((x+w/2,y+h/2),self.CENTER))
            elif s.kind in ("circle","hole"):
                pts.append(((s.cx,s.cy),self.CENTER))
                for p in [(s.cx+s.r,s.cy),(s.cx-s.r,s.cy),(s.cx,s.cy+s.r),(s.cx,s.cy-s.r)]:
                    pts.append((p,self.ENDPOINT))
            elif s.kind=="ellipse":
                pts.append(((s.cx,s.cy),self.CENTER))
                for p in [(s.cx+s.rx,s.cy),(s.cx-s.rx,s.cy),(s.cx,s.cy+s.ry),(s.cx,s.cy-s.ry)]:
                    pts.append((p,self.ENDPOINT))
            elif s.kind=="line":
                pts.append(((s.x1,s.y1),self.ENDPOINT))
                pts.append(((s.x2,s.y2),self.ENDPOINT))
                pts.append((((s.x1+s.x2)/2,(s.y1+s.y2)/2),self.MIDPOINT))
        return pts
    def snap(self, mx, my, shapes, scale):
        tol=self.tol_px/scale
        best_d,best_pt,best_kind=tol+1,None,None
        if self.object_snap:
            for (px,py),kind in self.snap_points(shapes):
                d=math.hypot(mx-px,my-py)
                if d<best_d:
                    best_d,best_pt,best_kind=d,(px,py),kind
        if best_pt:
            return best_pt[0],best_pt[1],best_kind
        if self.grid_snap:
            gs=self.grid_size
            return round(mx/gs)*gs,round(my/gs)*gs,self.GRID
        return mx,my,None

class AlignGuides:
    def __init__(self): self.tol_mm=0.5
    def get_guides(self, mx, my, shapes):
        guides=[]
        for s in shapes:
            if s.kind=="rect":
                for rx in [s.x,s.x+s.w/2,s.x+s.w]:
                    if abs(mx-rx)<self.tol_mm: guides.append(("v",rx))
                for ry in [s.y,s.y+s.h/2,s.y+s.h]:
                    if abs(my-ry)<self.tol_mm: guides.append(("h",ry))
            elif s.kind in ("circle","hole","ellipse"):
                if abs(mx-s.cx)<self.tol_mm: guides.append(("v",s.cx))
                if abs(my-s.cy)<self.tol_mm: guides.append(("h",s.cy))
        return guides

class DrawingCanvas(tk.Canvas):
    HANDLE_R=5
    COLORS={"rect":"#1565C0","circle":"#1565C0","ellipse":"#1565C0","hole":"#e53935","line":"#2e7d32"}
    FILL={"rect":"#E3F2FD","circle":"#E3F2FD","ellipse":"#E3F2FD","hole":"#FFEBEE","line":""}

    def __init__(self, master, on_select_cb=None, on_change_cb=None, coord_cb=None, **kw):
        # bg 기본값 설정 (중복 방지)
        kw.setdefault("bg", "#1e2a35")
        kw.setdefault("cursor", "crosshair")
        super().__init__(master, **kw)
        self.shapes=[]; self.selected=None; self.tool="select"
        self.scale=1.5; self.offset=[60,60]
        self.on_select_cb=on_select_cb; self.on_change_cb=on_change_cb; self.coord_cb=coord_cb
        self.snap_sys=SnapSystem(); self.guides=AlignGuides(); self.ortho=False
        self._drag_start=None; self._drag_shape_orig=None
        self._draw_start=None; self._temp_ids=[]; self._cur_mm=(0.0,0.0); self._snap_kind=None
        self._pan_origin=None; self._pan_offset_orig=None
        self.bind("<ButtonPress-1>",self._on_press)
        self.bind("<B1-Motion>",self._on_drag)
        self.bind("<ButtonRelease-1>",self._on_release)
        self.bind("<Motion>",self._on_move)
        self.bind("<Delete>",self._delete_selected)
        self.bind("<BackSpace>",self._delete_selected)
        self.bind("<KeyPress-Shift_L>",lambda e:setattr(self,"ortho",True))
        self.bind("<KeyRelease-Shift_L>",lambda e:setattr(self,"ortho",False))
        self.bind("<KeyPress-Shift_R>",lambda e:setattr(self,"ortho",True))
        self.bind("<KeyRelease-Shift_R>",lambda e:setattr(self,"ortho",False))
        self.bind("<MouseWheel>",self._on_wheel)
        self.bind("<ButtonPress-2>",self._pan_start)
        self.bind("<B2-Motion>",self._pan_move)
        self.focus_set()
        self.after(100,self._draw_grid)

    def mm2px(self,v): return v*self.scale
    def mm_to_canvas(self,x,y): return(self.offset[0]+x*self.scale,self.offset[1]+y*self.scale)
    def canvas_to_mm(self,cx,cy): return((cx-self.offset[0])/self.scale,(cy-self.offset[1])/self.scale)

    def _apply_snap(self,cx,cy):
        mx,my=self.canvas_to_mm(cx,cy)
        sx,sy,kind=self.snap_sys.snap(mx,my,self.shapes,self.scale)
        self._snap_kind=kind
        if self.ortho and self._draw_start:
            ox,oy=self._draw_start
            if abs(sx-ox)>=abs(sy-oy): sy=oy
            else: sx=ox
        return sx,sy

    def _draw_grid(self):
        self.delete("grid")
        w=self.winfo_width() or 800
        h=self.winfo_height() or 600
        if self.scale<=0: return
        gs=max(0.5,self.snap_sys.grid_size*self.scale)
        ox,oy=self.offset
        major=gs*10
        x=ox%gs
        while x<=w:
            col="#2d4a5a" if abs((x-ox)%major)<0.5 else "#223344"
            self.create_line(x,0,x,h,fill=col,width=1,tags="grid")
            x+=gs
        y=oy%gs
        while y<=h:
            col="#2d4a5a" if abs((y-oy)%major)<0.5 else "#223344"
            self.create_line(0,y,w,y,fill=col,width=1,tags="grid")
            y+=gs
        oxc,oyc=self.mm_to_canvas(0,0)
        self.create_line(oxc,0,oxc,h,fill="#3a5a6a",width=1,dash=(6,4),tags="grid")
        self.create_line(0,oyc,w,oyc,fill="#3a5a6a",width=1,dash=(6,4),tags="grid")
        self.tag_lower("grid")

    def redraw(self):
        self.delete("shape"); self.delete("dim"); self.delete("handle"); self.delete("guide")
        for s in self.shapes: self._draw_shape(s)
        if self.selected: self._draw_handles(self.selected)

    def _sc(self,s):
        b=self.COLORS.get(s.kind,"#1565C0")
        return "#FF6D00" if s.selected else b
    def _sf(self,s):
        return "#334455" if s.selected else self.FILL.get(s.kind,"")

    def _draw_shape(self,s):
        oc=self._sc(s); fc=self._sf(s); lw=2 if s.selected else 1.5
        if s.kind=="rect":
            x1,y1=self.mm_to_canvas(s.x,s.y); x2,y2=self.mm_to_canvas(s.x+s.w,s.y+s.h)
            self.create_rectangle(x1,y1,x2,y2,outline=oc,fill=fc,width=lw,tags="shape")
            self._draw_dims(s)
        elif s.kind in ("circle","hole"):
            cx,cy=self.mm_to_canvas(s.cx,s.cy); r=self.mm2px(s.r)
            self.create_oval(cx-r,cy-r,cx+r,cy+r,outline=oc,fill=fc,width=lw,tags="shape")
        elif s.kind=="ellipse":
            cx,cy=self.mm_to_canvas(s.cx,s.cy); rx=self.mm2px(s.rx); ry=self.mm2px(s.ry)
            self.create_oval(cx-rx,cy-ry,cx+rx,cy+ry,outline=oc,fill=fc,width=lw,tags="shape")
        elif s.kind=="line":
            x1,y1=self.mm_to_canvas(s.x1,s.y1); x2,y2=self.mm_to_canvas(s.x2,s.y2)
            self.create_line(x1,y1,x2,y2,fill=oc,width=lw,arrow="last",tags="shape")

    def _draw_dims(self,s):
        if s.kind!="rect": return
        x1c,y1c=self.mm_to_canvas(s.x,s.y); x2c,y2c=self.mm_to_canvas(s.x+s.w,s.y+s.h)
        off=12; mx=(x1c+x2c)/2
        self.create_line(x1c,y2c+off,x2c,y2c+off,fill="#607080",width=1,tags="dim")
        self.create_line(x1c,y2c,x1c,y2c+off,fill="#607080",width=1,tags="dim")
        self.create_line(x2c,y2c,x2c,y2c+off,fill="#607080",width=1,tags="dim")
        self.create_text(mx,y2c+off+7,text="%.1f"%s.w,fill="#90CAF9",font=("Consolas",7),tags="dim")
        my=(y1c+y2c)/2
        self.create_line(x2c+off,y1c,x2c+off,y2c,fill="#607080",width=1,tags="dim")
        self.create_line(x2c,y1c,x2c+off,y1c,fill="#607080",width=1,tags="dim")
        self.create_line(x2c,y2c,x2c+off,y2c,fill="#607080",width=1,tags="dim")
        self.create_text(x2c+off+14,my,text="%.1f"%s.h,fill="#90CAF9",font=("Consolas",7),tags="dim")

    def _draw_handles(self,s):
        r=self.HANDLE_R; pts=[]
        if s.kind=="rect":
            for px,py in [(s.x,s.y),(s.x+s.w,s.y),(s.x+s.w,s.y+s.h),(s.x,s.y+s.h)]:
                cx,cy=self.mm_to_canvas(px,py); pts.append((cx,cy))
        elif s.kind in ("circle","hole"):
            cx,cy=self.mm_to_canvas(s.cx,s.cy); pts=[(cx,cy)]
        elif s.kind=="ellipse":
            cx,cy=self.mm_to_canvas(s.cx,s.cy); pts=[(cx,cy)]
        elif s.kind=="line":
            cx1,cy1=self.mm_to_canvas(s.x1,s.y1); cx2,cy2=self.mm_to_canvas(s.x2,s.y2)
            pts=[(cx1,cy1),(cx2,cy2)]
        for cx,cy in pts:
            self.create_rectangle(cx-r,cy-r,cx+r,cy+r,fill="#FF6D00",outline="white",width=1,tags="handle")

    def _show_snap(self,sx,sy,kind):
        for tid in self._temp_ids: self.delete(tid)
        self._temp_ids=[]
        if kind is None: return
        cx,cy=self.mm_to_canvas(sx,sy); r=8
        col={"endpoint":"#FFD600","midpoint":"#00E5FF","center":"#69F0AE","grid":"#607080"}.get(kind,"white")
        self._temp_ids.append(self.create_oval(cx-r,cy-r,cx+r,cy+r,outline=col,width=2,tags="snap"))

    def _show_guides(self,mx,my):
        self.delete("guide")
        w=self.winfo_width() or 800; h=self.winfo_height() or 600
        for gt,val in self.guides.get_guides(mx,my,self.shapes):
            if gt=="v":
                cx,_=self.mm_to_canvas(val,0)
                self.create_line(cx,0,cx,h,fill="#00BCD4",dash=(4,4),width=1,tags="guide")
            else:
                _,cy=self.mm_to_canvas(0,val)
                self.create_line(0,cy,w,cy,fill="#00BCD4",dash=(4,4),width=1,tags="guide")

    def fit_view(self):
        if not self.shapes:
            self.offset=[60,60]; self.scale=1.5; self._draw_grid(); self.redraw(); return
        xs,ys=[],[]
        for s in self.shapes:
            if s.kind=="rect": xs+=[s.x,s.x+s.w]; ys+=[s.y,s.y+s.h]
            elif s.kind in ("circle","hole"): xs+=[s.cx-s.r,s.cx+s.r]; ys+=[s.cy-s.r,s.cy+s.r]
            elif s.kind=="ellipse": xs+=[s.cx-s.rx,s.cx+s.rx]; ys+=[s.cy-s.ry,s.cy+s.ry]
            elif s.kind=="line": xs+=[s.x1,s.x2]; ys+=[s.y1,s.y2]
        if not xs: return
        mnx,mny=min(xs),min(ys); rng_x=max(xs)-mnx; rng_y=max(ys)-mny
        w=self.winfo_width() or 800; h=self.winfo_height() or 600; pad=60
        if rng_x>0 and rng_y>0:
            self.scale=min((w-2*pad)/rng_x,(h-2*pad)/rng_y)
        self.offset=[pad-mnx*self.scale,pad-mny*self.scale]
        self._draw_grid(); self.redraw()

    def _on_move(self,e):
        sx,sy=self._apply_snap(e.x,e.y); self._cur_mm=(sx,sy)
        self._show_snap(sx,sy,self._snap_kind); self._show_guides(sx,sy)
        if self.coord_cb: self.coord_cb(sx,sy,self._snap_kind)
        if self._draw_start and self.tool!="select": self._update_preview(sx,sy)

    def _on_press(self,e):
        self.focus_set(); sx,sy=self._apply_snap(e.x,e.y)
        if self.tool=="select":
            hit=self._hit_test(sx,sy)
            for s in self.shapes: s.selected=(s is hit)
            self.selected=hit; self.redraw()
            if self.on_select_cb: self.on_select_cb(hit)
            if hit:
                self._drag_start=(sx,sy)
                if hit.kind=="rect": self._drag_shape_orig=(hit.x,hit.y)
                elif hit.kind in ("circle","hole"): self._drag_shape_orig=(hit.cx,hit.cy)
                elif hit.kind=="ellipse": self._drag_shape_orig=(hit.cx,hit.cy)
                elif hit.kind=="line": self._drag_shape_orig=(hit.x1,hit.y1,hit.x2,hit.y2)
        else:
            self._draw_start=(sx,sy)

    def _on_drag(self,e):
        sx,sy=self._apply_snap(e.x,e.y)
        if self.tool=="select" and self.selected and self._drag_start:
            dx=sx-self._drag_start[0]; dy=sy-self._drag_start[1]; s=self.selected
            if s.kind=="rect": s.x=self._drag_shape_orig[0]+dx; s.y=self._drag_shape_orig[1]+dy
            elif s.kind in ("circle","hole"): s.cx=self._drag_shape_orig[0]+dx; s.cy=self._drag_shape_orig[1]+dy
            elif s.kind=="ellipse": s.cx=self._drag_shape_orig[0]+dx; s.cy=self._drag_shape_orig[1]+dy
            elif s.kind=="line":
                orig=self._drag_shape_orig
                s.x1=orig[0]+dx; s.y1=orig[1]+dy; s.x2=orig[2]+dx; s.y2=orig[3]+dy
            self._draw_grid(); self.redraw()

    def _on_release(self,e):
        if self.tool!="select" and self._draw_start:
            sx,sy=self._apply_snap(e.x,e.y); x0,y0=self._draw_start
            self._finish_draw(x0,y0,sx,sy); self._draw_start=None
            for tid in self._temp_ids: self.delete(tid)
            self._temp_ids=[]
        if self.tool=="select" and self._drag_start:
            self._drag_start=None
            if self.on_change_cb: self.on_change_cb()

    def _update_preview(self,sx,sy):
        for tid in self._temp_ids: self.delete(tid)
        self._temp_ids=[]
        x0,y0=self._draw_start
        x1c,y1c=self.mm_to_canvas(x0,y0); x2c,y2c=self.mm_to_canvas(sx,sy); col="#90CAF9"
        if self.tool=="rect":
            self._temp_ids.append(self.create_rectangle(x1c,y1c,x2c,y2c,outline=col,dash=(4,3),tags="temp"))
        elif self.tool in ("circle","hole"):
            r=self.mm2px(math.hypot(sx-x0,sy-y0))
            self._temp_ids.append(self.create_oval(x1c-r,y1c-r,x1c+r,y1c+r,outline=col,dash=(4,3),tags="temp"))
        elif self.tool=="ellipse":
            rx=self.mm2px(abs(sx-x0)); ry=self.mm2px(abs(sy-y0))
            self._temp_ids.append(self.create_oval(x1c-rx,y1c-ry,x1c+rx,y1c+ry,outline=col,dash=(4,3),tags="temp"))
        elif self.tool=="line":
            self._temp_ids.append(self.create_line(x1c,y1c,x2c,y2c,fill=col,dash=(4,3),tags="temp"))

    def _finish_draw(self,x0,y0,x1,y1):
        s=None
        if self.tool=="rect":
            x=min(x0,x1); y=min(y0,y1); w=abs(x1-x0); h=abs(y1-y0)
            if w<0.1 or h<0.1: return
            s=RectShape(x,y,w,h)
        elif self.tool=="circle":
            r=math.hypot(x1-x0,y1-y0)
            if r<0.1: return
            s=CircleShape(x0,y0,r)
        elif self.tool=="hole":
            r=math.hypot(x1-x0,y1-y0)
            if r<0.1: return
            s=HoleShape(x0,y0,r)
        elif self.tool=="ellipse":
            rx=abs(x1-x0); ry=abs(y1-y0)
            if rx<0.1 or ry<0.1: return
            s=EllipseShape(x0,y0,rx,ry)
        elif self.tool=="line":
            if math.hypot(x1-x0,y1-y0)<0.1: return
            s=LineShape(x0,y0,x1,y1)
        if s:
            self.shapes.append(s); self.redraw()
            if self.on_change_cb: self.on_change_cb()

    def _hit_test(self,mx,my):
        tol=5/self.scale
        for s in reversed(self.shapes):
            if s.kind=="rect":
                if s.x-tol<=mx<=s.x+s.w+tol and s.y-tol<=my<=s.y+s.h+tol: return s
            elif s.kind in ("circle","hole"):
                if math.hypot(mx-s.cx,my-s.cy)<=s.r+tol: return s
            elif s.kind=="ellipse":
                if s.rx>0 and s.ry>0:
                    dx=(mx-s.cx)/s.rx; dy=(my-s.cy)/s.ry
                    if dx*dx+dy*dy<=(1+tol/min(s.rx,s.ry))**2: return s
            elif s.kind=="line":
                if self._pld(mx,my,s.x1,s.y1,s.x2,s.y2)<=tol: return s
        return None

    def _pld(self,px,py,x1,y1,x2,y2):
        dx=x2-x1; dy=y2-y1
        if dx==0 and dy==0: return math.hypot(px-x1,py-y1)
        t=max(0,min(1,((px-x1)*dx+(py-y1)*dy)/(dx*dx+dy*dy)))
        return math.hypot(px-(x1+t*dx),py-(y1+t*dy))

    def _delete_selected(self,e=None):
        if self.selected:
            self.shapes.remove(self.selected); self.selected=None; self.redraw()
            if self.on_select_cb: self.on_select_cb(None)
            if self.on_change_cb: self.on_change_cb()

    def _on_wheel(self,e):
        factor=1.1 if e.delta>0 else 0.9
        mx,my=self.canvas_to_mm(e.x,e.y); self.scale*=factor
        self.scale=max(0.2,min(self.scale,20.0))
        self.offset[0]=e.x-mx*self.scale; self.offset[1]=e.y-my*self.scale
        self._draw_grid(); self.redraw()

    def _pan_start(self,e): self._pan_origin=(e.x,e.y); self._pan_offset_orig=list(self.offset)
    def _pan_move(self,e):
        if self._pan_origin:
            dx=e.x-self._pan_origin[0]; dy=e.y-self._pan_origin[1]
            self.offset[0]=self._pan_offset_orig[0]+dx; self.offset[1]=self._pan_offset_orig[1]+dy
            self._draw_grid(); self.redraw()

    def total_perimeter_mm(self): return sum(s.perimeter_mm() for s in self.shapes)


class PropertiesPanel(tk.Frame):
    def __init__(self,master,canvas_w,on_change_cb=None,**kw):
        kw.setdefault("bg","#1e2a35"); super().__init__(master,**kw)
        self.canvas_w=canvas_w; self.on_change_cb=on_change_cb
        self._vars={}; self._entries={}; self._shape=None
        self._inner=tk.Frame(self,bg="#1e2a35"); self._inner.pack(fill="both",expand=True)
    def load(self,shape):
        for w in self._inner.winfo_children(): w.destroy()
        self._vars={}; self._entries={}; self._shape=shape
        if shape is None:
            tk.Label(self._inner,text="도형을 선택하세요",bg="#1e2a35",fg="#607080",font=("Malgun Gothic",8)).pack(pady=10)
            return
        fields=self._fields(shape)
        for i,(label,attr,vtype) in enumerate(fields):
            row=tk.Frame(self._inner,bg="#1e2a35"); row.pack(fill="x",padx=4,pady=2)
            tk.Label(row,text=label,bg="#1e2a35",fg="#aabbcc",font=("Malgun Gothic",8),width=6,anchor="e").pack(side="left",padx=(0,4))
            v=tk.StringVar(value=str(round(getattr(shape,attr),3)))
            e=tk.Entry(row,textvariable=v,width=10,bg="#263545",fg="white",insertbackground="white",font=("Malgun Gothic",8),relief="flat")
            e.pack(side="left")
            self._vars[attr]=v; self._entries[attr]=(e,vtype)
        tk.Button(self._inner,text="Apply",command=self._apply,bg="#1565C0",fg="white",relief="flat",font=("Malgun Gothic",8),padx=10).pack(pady=6)
    def _fields(self,s):
        if s.kind=="rect": return[("X(mm)","x",float),("Y(mm)","y",float),("W(mm)","w",float),("H(mm)","h",float)]
        elif s.kind in ("circle","hole"): return[("CX","cx",float),("CY","cy",float),("R(mm)","r",float)]
        elif s.kind=="ellipse": return[("CX","cx",float),("CY","cy",float),("RX","rx",float),("RY","ry",float)]
        elif s.kind=="line": return[("X1","x1",float),("Y1","y1",float),("X2","x2",float),("Y2","y2",float)]
        return[]
    def _apply(self):
        if not self._shape: return
        try:
            for attr,(e,vtype) in self._entries.items(): setattr(self._shape,attr,vtype(self._vars[attr].get()))
            self.canvas_w.redraw()
            if self.on_change_cb: self.on_change_cb()
        except ValueError: messagebox.showerror("Error","Please enter a number.")


class DimInputPanel(tk.Frame):
    def __init__(self,master,canvas_w,**kw):
        kw.setdefault("bg","#1e2a35"); super().__init__(master,**kw)
        self.canvas_w=canvas_w; self._build()
    def _build(self):
        tk.Label(self,text="Add Shape (mm)",bg="#263545",fg="#90CAF9",font=("Malgun Gothic",8,"bold"),anchor="w",padx=6).pack(fill="x",pady=(2,2))
        f=tk.Frame(self,bg="#1e2a35"); f.pack(fill="x",padx=4)
        self.kind_var=tk.StringVar(value="rect")
        for val,lbl in[("rect","Rect"),("circle","Circle"),("ellipse","Ellipse"),("hole","Hole"),("line","Line")]:
            tk.Radiobutton(f,text=lbl,variable=self.kind_var,value=val,bg="#1e2a35",fg="#ccdde0",selectcolor="#263545",activebackground="#1e2a35",activeforeground="white",font=("Malgun Gothic",7),command=self._update_fields).pack(side="left")
        self.fields_frame=tk.Frame(self,bg="#1e2a35"); self.fields_frame.pack(fill="x",padx=4)
        self._field_vars={}; self._update_fields()
        tk.Button(self,text="Add",command=self._add,bg="#1565C0",fg="white",relief="flat",font=("Malgun Gothic",8),padx=8).pack(pady=4)
    def _update_fields(self):
        for w in self.fields_frame.winfo_children(): w.destroy()
        self._field_vars={}
        specs={"rect":[("X","x","0"),("Y","y","0"),("W","w","50"),("H","h","30")],"circle":[("CX","cx","30"),("CY","cy","30"),("R","r","20")],"ellipse":[("CX","cx","30"),("CY","cy","30"),("RX","rx","25"),("RY","ry","15")],"hole":[("CX","cx","30"),("CY","cy","30"),("R","r","5")],"line":[("X1","x1","0"),("Y1","y1","0"),("X2","x2","50"),("Y2","y2","0")]}
        for label,attr,default in specs.get(self.kind_var.get(),[]):
            row=tk.Frame(self.fields_frame,bg="#1e2a35"); row.pack(fill="x",pady=1)
            tk.Label(row,text=label+":",bg="#1e2a35",fg="#aabbcc",font=("Malgun Gothic",7),width=4,anchor="e").pack(side="left")
            v=tk.StringVar(value=default)
            tk.Entry(row,textvariable=v,width=7,bg="#263545",fg="white",insertbackground="white",font=("Malgun Gothic",7),relief="flat").pack(side="left",padx=2)
            self._field_vars[attr]=v
    def _add(self):
        kind=self.kind_var.get()
        try: vals={k:float(v.get()) for k,v in self._field_vars.items()}
        except ValueError: messagebox.showerror("Error","Please enter a number."); return
        m={"rect":RectShape,"circle":CircleShape,"ellipse":EllipseShape,"hole":HoleShape,"line":LineShape}
        s=m[kind](**vals); self.canvas_w.shapes.append(s); self.canvas_w.redraw()
        if self.canvas_w.on_change_cb: self.canvas_w.on_change_cb()


class CuttingRow:
    def __init__(self,parent,remove_cb,update_cb):
        self.frame=tk.Frame(parent,bg="#1e2a35"); self.frame.pack(fill="x",pady=1)
        self.name_var=tk.StringVar(value="Cutting"); self.price_var=tk.StringVar(value="0")
        tk.Entry(self.frame,textvariable=self.name_var,width=9,bg="#263545",fg="white",insertbackground="white",font=("Malgun Gothic",8),relief="flat").pack(side="left",padx=(0,2))
        tk.Entry(self.frame,textvariable=self.price_var,width=8,bg="#263545",fg="white",insertbackground="white",font=("Malgun Gothic",8),relief="flat").pack(side="left")
        tk.Label(self.frame,text="won/m",bg="#1e2a35",fg="#aabbcc",font=("Malgun Gothic",7)).pack(side="left",padx=2)
        tk.Button(self.frame,text="X",command=lambda:remove_cb(self),bg="#b71c1c",fg="white",relief="flat",font=("Malgun Gothic",7),padx=3).pack(side="right")
        self.name_var.trace_add("write",lambda *a:update_cb())
        self.price_var.trace_add("write",lambda *a:update_cb())
    def get_price(self):
        try: return float(self.price_var.get())
        except: return 0.0
    def to_dict(self): return{"name":self.name_var.get(),"price":self.price_var.get()}
    def from_dict(self,d): self.name_var.set(d.get("name","")); self.price_var.set(d.get("price","0"))


class CeramicCostApp:
    def __init__(self,root):
        self.root=root; self.root.title("Ceramic Cost Calculator v3")
        self.root.geometry("1200x780"); self.root.minsize(950,620)
        self.root.configure(bg="#151f28"); self.cutting_rows=[]
        self._build_ui(); self._load_data()

    def _build_ui(self):
        tk.Label(self.root,text="  Ceramic Cost Calculator v3",font=("Malgun Gothic",12,"bold"),bg="#0d47a1",fg="white",pady=8).pack(fill="x")
        main=tk.Frame(self.root,bg="#151f28"); main.pack(fill="both",expand=True)

        # Left panel
        left=tk.Frame(main,bg="#1e2a35",width=215); left.pack(side="left",fill="y",padx=(6,3),pady=6); left.pack_propagate(False)
        tk.Label(left,text="Tool",bg="#263545",fg="#90CAF9",font=("Malgun Gothic",8,"bold"),anchor="w",padx=6).pack(fill="x",pady=(6,2))
        self.tool_var=tk.StringVar(value="select")
        tf=tk.Frame(left,bg="#1e2a35"); tf.pack(fill="x",padx=4)
        for lbl,val in [("Select","select"),("Rectangle","rect"),("Circle","circle"),("Ellipse","ellipse"),("Hole","hole"),("Line","line")]:
            tk.Radiobutton(tf,text=lbl,variable=self.tool_var,value=val,bg="#1e2a35",fg="#ccdde0",selectcolor="#263545",activebackground="#1e2a35",activeforeground="white",font=("Malgun Gothic",8),command=self._set_tool).pack(anchor="w")
        ttk.Separator(left,orient="horizontal").pack(fill="x",pady=4)
        tk.Label(left,text="Snap Settings",bg="#263545",fg="#90CAF9",font=("Malgun Gothic",8,"bold"),anchor="w",padx=6).pack(fill="x",pady=(2,2))
        sf=tk.Frame(left,bg="#1e2a35"); sf.pack(fill="x",padx=4)
        self.grid_snap_var=tk.BooleanVar(value=True); self.obj_snap_var=tk.BooleanVar(value=True)
        for text,var,attr in[("Grid Snap",self.grid_snap_var,"grid_snap"),("Object Snap",self.obj_snap_var,"object_snap")]:
            tk.Checkbutton(sf,text=text,variable=var,command=lambda a=attr,v=var:self._toggle_snap(a,v),bg="#1e2a35",fg="#ccdde0",selectcolor="#263545",activebackground="#1e2a35",activeforeground="white",font=("Malgun Gothic",8)).pack(anchor="w")
        gf=tk.Frame(left,bg="#1e2a35"); gf.pack(fill="x",padx=4,pady=2)
        tk.Label(gf,text="Grid(mm):",bg="#1e2a35",fg="#aabbcc",font=("Malgun Gothic",7)).pack(side="left")
        self.grid_size_var=tk.StringVar(value="5")
        tk.Entry(gf,textvariable=self.grid_size_var,width=5,bg="#263545",fg="white",insertbackground="white",font=("Malgun Gothic",8),relief="flat").pack(side="left",padx=3)
        tk.Button(gf,text="Apply",command=self._apply_grid,bg="#37474f",fg="white",relief="flat",font=("Malgun Gothic",7),padx=4).pack(side="left")
        ttk.Separator(left,orient="horizontal").pack(fill="x",pady=4)
        self._dim_pp=tk.Frame(left,bg="#1e2a35"); self._dim_pp.pack(fill="x")
        ttk.Separator(left,orient="horizontal").pack(fill="x",pady=4)
        tk.Label(left,text="Shape Properties",bg="#263545",fg="#90CAF9",font=("Malgun Gothic",8,"bold"),anchor="w",padx=6).pack(fill="x",pady=(2,2))
        self._prop_pp=tk.Frame(left,bg="#1e2a35"); self._prop_pp.pack(fill="both",expand=True)

        # Center canvas
        center=tk.Frame(main,bg="#151f28"); center.pack(side="left",fill="both",expand=True,pady=6)
        cbar=tk.Frame(center,bg="#151f28"); cbar.pack(fill="x",padx=4)
        for text,cmd,cbg in[("Clear All",self._clear_all,"#b71c1c"),("Fit View",lambda:self.canvas_w.fit_view(),"#37474f")]:
            tk.Button(cbar,text=text,command=cmd,bg=cbg,fg="white",relief="flat",font=("Malgun Gothic",8),padx=7,pady=3).pack(side="left",padx=2)
        tk.Label(cbar,text="Shift=Ortho  /  Wheel=Zoom  /  Mid=Pan  /  Del=Delete",bg="#151f28",fg="#607080",font=("Malgun Gothic",7)).pack(side="left",padx=12)
        self.canvas_w=DrawingCanvas(center,on_select_cb=self._on_sel,on_change_cb=self._on_change,coord_cb=self._on_coord)
        self.canvas_w.pack(fill="both",expand=True,padx=4,pady=(2,0))
        stat=tk.Frame(center,bg="#0d1a22",height=22); stat.pack(fill="x",padx=4); stat.pack_propagate(False)
        self.coord_lbl=tk.Label(stat,text="X: 0.000  Y: 0.000",bg="#0d1a22",fg="#5BC8F5",font=("Consolas",8),anchor="w",padx=8); self.coord_lbl.pack(side="left",fill="y")
        self.snap_lbl=tk.Label(stat,text="",bg="#0d1a22",fg="#FFD600",font=("Malgun Gothic",7),anchor="w"); self.snap_lbl.pack(side="left",fill="y")
        self.cut_stat_lbl=tk.Label(stat,text="Total cut: 0.000 mm",bg="#0d1a22",fg="#A5D6A7",font=("Consolas",8),anchor="e",padx=8); self.cut_stat_lbl.pack(side="right",fill="y")
        self.dim_panel=DimInputPanel(self._dim_pp,self.canvas_w); self.dim_panel.pack(fill="x")
        self.prop_panel=PropertiesPanel(self._prop_pp,self.canvas_w,on_change_cb=self._on_change); self.prop_panel.pack(fill="both",expand=True)

        # Right panel
        ro=tk.Frame(main,bg="#1e2a35",width=265); ro.pack(side="right",fill="y",padx=(3,6),pady=6); ro.pack_propagate(False)
        rc=tk.Canvas(ro,bg="#1e2a35",highlightthickness=0)
        rs=ttk.Scrollbar(ro,orient="vertical",command=rc.yview)
        self.rf=tk.Frame(rc,bg="#1e2a35")
        self.rf.bind("<Configure>",lambda e:rc.configure(scrollregion=rc.bbox("all")))
        rc.create_window((0,0),window=self.rf,anchor="nw"); rc.configure(yscrollcommand=rs.set)
        rs.pack(side="right",fill="y"); rc.pack(fill="both",expand=True)
        def _scrl(e): rc.yview_scroll(int(-1*(e.delta/120)),"units")
        rc.bind("<MouseWheel>",_scrl); self.rf.bind("<MouseWheel>",_scrl)

        self._sec("1. Product Info"); c1=self._card()
        for ri,(lbl,attr,dflt) in enumerate([("Product","product_var",""),("Material","material_var",""),("Quantity","qty_var","1")]):
            tk.Label(c1,text=lbl+":",bg="#1e2a35",fg="#aabbcc",font=("Malgun Gothic",8),anchor="e",width=8).grid(row=ri,column=0,sticky="e",padx=(6,2),pady=3)
            v=tk.StringVar(value=dflt); setattr(self,attr,v)
            tk.Entry(c1,textvariable=v,width=17,bg="#263545",fg="white",insertbackground="white",font=("Malgun Gothic",8),relief="flat").grid(row=ri,column=1,sticky="w",padx=(0,6),pady=3)

        self._sec("2. Cutting Process (won/m)"); self.cut_frame=self._card()
        tk.Label(self.cut_frame,text="Name        Price(won/m)",bg="#1e2a35",fg="#607080",font=("Malgun Gothic",7)).pack(anchor="w",padx=4,pady=(2,0))
        self._add_cut()
        bf=tk.Frame(self.rf,bg="#1e2a35"); bf.pack(fill="x",padx=4)
        tk.Button(bf,text="+ Add Process",command=self._add_cut,bg="#263545",fg="#90CAF9",relief="flat",font=("Malgun Gothic",8)).pack(side="left",pady=2)

        self._sec("3. Other Costs"); c3=self._card()
        for ri,(lbl,attr,dflt) in enumerate([("Material(won)","mat_var","0"),("Other(won)","other_var","0"),("Overhead(%)","overhead_var","15"),("Profit(%)","profit_var","20")]):
            tk.Label(c3,text=lbl+":",bg="#1e2a35",fg="#aabbcc",font=("Malgun Gothic",8),anchor="e",width=11).grid(row=ri,column=0,sticky="e",padx=(6,2),pady=3)
            v=tk.StringVar(value=dflt); setattr(self,attr,v)
            tk.Entry(c3,textvariable=v,width=11,bg="#263545",fg="white",insertbackground="white",font=("Malgun Gothic",8),relief="flat").grid(row=ri,column=1,sticky="w",padx=(0,6),pady=3)
            v.trace_add("write",lambda *a:self._update_cost())

        self._sec("4. Total"); cf=self._card()
        self.sum_labels={}
        for ri,(key,kor) in enumerate([("cutting","Cutting"),("material","Material"),("other","Other"),("overhead","Overhead"),("profit","Profit"),("total","TOTAL (won)")]):
            tk.Label(cf,text=kor+":",bg="#1e2a35",fg="#aabbcc",font=("Malgun Gothic",8),anchor="e",width=11).grid(row=ri,column=0,sticky="e",padx=(6,2),pady=2)
            lbl=tk.Label(cf,text="0",bg="#1e2a35",fg="#FFD600" if key=="total" else "white",font=("Malgun Gothic",9 if key=="total" else 8,"bold" if key=="total" else "normal"),anchor="e",width=12)
            lbl.grid(row=ri,column=1,sticky="e",padx=(0,6),pady=2); self.sum_labels[key]=lbl

        btnf=tk.Frame(self.rf,bg="#1e2a35"); btnf.pack(fill="x",padx=4,pady=8)
        tk.Button(btnf,text="Save",command=self._save_data,bg="#1565C0",fg="white",relief="flat",font=("Malgun Gothic",9),padx=14,pady=5).pack(side="left",padx=3)
        tk.Button(btnf,text="Reset",command=self._reset,bg="#37474f",fg="white",relief="flat",font=("Malgun Gothic",9),padx=14,pady=5).pack(side="left",padx=3)

    def _sec(self,text): tk.Label(self.rf,text=text,bg="#1e2a35",fg="#5BC8F5",font=("Malgun Gothic",8,"bold")).pack(anchor="w",padx=4,pady=(8,2))
    def _card(self):
        f=tk.Frame(self.rf,bg="#1e2a35",relief="groove",bd=1); f.pack(fill="x",padx=4,pady=2); return f

    def _set_tool(self): self.canvas_w.tool=self.tool_var.get()
    def _toggle_snap(self,attr,var): setattr(self.canvas_w.snap_sys,attr,var.get())
    def _apply_grid(self):
        try:
            v=float(self.grid_size_var.get())
            if v<=0: raise ValueError
            self.canvas_w.snap_sys.grid_size=v; self.canvas_w._draw_grid()
        except ValueError: messagebox.showerror("Error","Enter a value greater than 0.")
    def _on_sel(self,shape): self.prop_panel.load(shape)
    def _on_change(self): self._update_cost(); self.prop_panel.load(self.canvas_w.selected)
    def _on_coord(self,x,y,snap_kind):
        self.coord_lbl.config(text="X: %.3f  Y: %.3f"%(x,y))
        names={"endpoint":"Endpoint","midpoint":"Midpoint","center":"Center","grid":"Grid"}
        self.snap_lbl.config(text=names.get(snap_kind,"") if snap_kind else "")
    def _add_cut(self):
        row=CuttingRow(self.cut_frame,self._remove_cut,self._update_cost); self.cutting_rows.append(row); self._update_cost()
    def _remove_cut(self,row): row.frame.destroy(); self.cutting_rows.remove(row); self._update_cost()
    def _clear_all(self):
        if not messagebox.askyesno("Clear All","Delete all shapes?"): return
        self.canvas_w.shapes.clear(); self.canvas_w.selected=None; self.prop_panel.load(None); self.canvas_w.redraw(); self._update_cost()
    def _update_cost(self):
        if not hasattr(self,'sum_labels'): return
        total_mm=self.canvas_w.total_perimeter_mm(); total_m=total_mm/1000.0
        self.cut_stat_lbl.config(text="Total cut: %.3f mm"%total_mm)
        cut_total=sum(r.get_price()*total_m for r in self.cutting_rows)
        def flt(v):
            try: return float(v.get())
            except: return 0.0
        mat=flt(self.mat_var); other=flt(self.other_var)
        try: qty=max(1,int(self.qty_var.get()))
        except: qty=1
        overhead_r=flt(self.overhead_var)/100.0; profit_r=flt(self.profit_var)/100.0
        cut_qty=cut_total*qty; mat_qty=mat*qty; other_qty=other*qty
        base=cut_qty+mat_qty+other_qty; overhead=base*overhead_r; subtotal=base+overhead
        profit=subtotal*profit_r; total=subtotal+profit
        self.sum_labels["cutting"].config(text="%,.0f"%cut_qty)
        self.sum_labels["material"].config(text="%,.0f"%mat_qty)
        self.sum_labels["other"].config(text="%,.0f"%other_qty)
        self.sum_labels["overhead"].config(text="%,.0f"%overhead)
        self.sum_labels["profit"].config(text="%,.0f"%profit)
        self.sum_labels["total"].config(text="%,.0f"%total)
    def _save_data(self):
        data={"product":self.product_var.get(),"material":self.material_var.get(),"qty":self.qty_var.get(),"mat":self.mat_var.get(),"other":self.other_var.get(),"overhead":self.overhead_var.get(),"profit":self.profit_var.get(),"cuttings":[r.to_dict() for r in self.cutting_rows],"shapes":[s.to_dict() for s in self.canvas_w.shapes]}
        try:
            with open(SAVE_FILE,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,indent=2)
            messagebox.showinfo("Saved","Saved successfully.")
        except Exception as ex: messagebox.showerror("Save Error",str(ex))
    def _load_data(self):
        if not os.path.exists(SAVE_FILE): return
        try:
            with open(SAVE_FILE,encoding="utf-8") as f: data=json.load(f)
            self.product_var.set(data.get("product","")); self.material_var.set(data.get("material",""))
            self.qty_var.set(data.get("qty","1")); self.mat_var.set(data.get("mat","0"))
            self.other_var.set(data.get("other","0")); self.overhead_var.set(data.get("overhead","15")); self.profit_var.set(data.get("profit","20"))
            cuts=data.get("cuttings",[])
            if cuts:
                for r in list(self.cutting_rows): r.frame.destroy()
                self.cutting_rows.clear()
                for cd in cuts: self._add_cut(); self.cutting_rows[-1].from_dict(cd)
            shapes=data.get("shapes",[])
            self.canvas_w.shapes=[Shape.from_dict(d) for d in shapes if d]
            self.canvas_w.redraw(); self._update_cost()
        except Exception: pass
    def _reset(self):
        if not messagebox.askyesno("Reset","Reset everything?"): return
        self.product_var.set(""); self.material_var.set(""); self.qty_var.set("1")
        self.mat_var.set("0"); self.other_var.set("0"); self.overhead_var.set("15"); self.profit_var.set("20")
        for r in list(self.cutting_rows): r.frame.destroy()
        self.cutting_rows.clear(); self._add_cut()
        self.canvas_w.shapes.clear(); self.canvas_w.selected=None
        self.prop_panel.load(None); self.canvas_w.redraw(); self._update_cost()


if __name__=="__main__":
    import traceback
    def _report_error(exc,val,tb):
        err="".join(traceback.format_exception(exc,val,tb))
        try:
            with open("error_log.txt","w",encoding="utf-8") as f: f.write(err)
        except: pass
        try: messagebox.showerror("Callback Error",err[:1000])
        except: pass
    try:
        root=tk.Tk(); root.report_callback_exception=_report_error
        app=CeramicCostApp(root); root.mainloop()
    except Exception:
        err=traceback.format_exc()
        try:
            with open("error_log.txt","w",encoding="utf-8") as f: f.write(err)
        except: pass
        try:
            r2=tk.Tk(); r2.withdraw(); messagebox.showerror("Startup Error",err[:1000]); r2.destroy()
        except: pass
